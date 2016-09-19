import datetime
import getpass
import os
import random

from fabric.state import output
from fabric.api import local, run, env, prefix, abort, sudo, task, get
from fabric.api import put, cd, prompt
from fabric.contrib.files import is_link, exists
from fabric.contrib.console import confirm

import requests

import fabsettings
import gittools


hooks = {}


env.use_ssh_config = True


def host_env_update():
    run_hooks("pre_host_env_update")
    run('virtualenv "{}"'.format(env.venv_path))
    with prefix(env.venv):
        run("pip install --upgrade -r {0}/requirements.txt".format(
            env.current_link))
    run_hooks("post_host_env_update")


def is_prod():
    return env.environment not in ["vagrant", "dev"]


def prod_check():
    skip_check = env.get('skip_check', "False") == "True"
    if skip_check is False and env.environment not in ["vagrant", "dev"]:
        number_1 = random.randint(1, 9)
        number_2 = random.randint(1, 9)
        print ("You are modifying %s. In order to be sure you "
               "really really mean it, please enter the answer to the "
               "question below"
               " or enter 'a' to abort:\n" % env.environment.upper())
        answer = prompt("What is %s + %s ?" % (number_1, number_2))

        if answer == "a":
            abort("Aborting")
        if answer != str(number_1 + number_2):
            abort("Incorrect Answer: Aborting")
        print "Correct Answer: Proceeding"


def vagrant():
    # use vagrant ssh key
    env.forward_agent = True
    result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1]
    if env.key_filename.startswith('"') or env.key_filename.startswith('\''):
        env.key_filename = env.key_filename[1:-1]


@task
def deploy(environment, gitref=None, **overrides):
    if environment == "vagrant":
        vagrant()

    fabsettings.dev_settings(environment)
    env.update(overrides)
    env.gitref = gitref
    _deploy()


@task
def release(environment, gitref="HEAD", version=None, **overrides):
    fabsettings.release_settings(environment, version, gitref)
    env.update(overrides)
    env.gitref = gitref
    _deploy()


def _deploy():
    env.commit_ref = get_commit_ref()

    confirm_settings()
    prod_check()
    archive_build()
#    link_dev_code()
    put_build_archives()
    extract_build_archives()
    create_links()
    host_env_update()
    collect_static()
    migrate_db()
    run_hooks("post_migrate")
    restart_uwsgi()
    run_hooks("post_restart")
    tag_build()
    put_version_txt()
    cleanup()


def add_hook(hook_name, hook):
    if hook_name not in hooks:
        hooks[hook_name] = [hook]
    else:
        hooks[hook_name].append(hook)


def run_hooks(hook_name):
    for hook in hooks.get(hook_name, []):
        hook()


def in_dev_mode():
    return env.environment == "vagrant" and env.get('dev_mode', False)


def link_dev_code():
    if in_dev_mode():
        if (exists(env.current_link) or is_link(env.current_link)):
            run("rm -rf {0}".format(env.current_link))
            run("ln -s /vagrant/ {0}".format(env.current_link))


def deploy_prod(environment, version, **overrides):
    fabsettings.production_settings(environment, version)
    env.update(overrides)
    env.gitref = version
    _deploy()


@task
def rollback(environment, buildid=None, **overrides):
    if environment == "vagrant":
        vagrant()
    if buildid is None:
        fabsettings.rollback_settings(environment, "previous")
        prod_check()
        _revert_deploy_links()
        restart_uwsgi()
    else:
        fabsettings.rollback_settings(environment, buildid)
        prod_check()
        env.build_folder = buildid
        env.environment = "rollback"
        fabsettings._global_settings()
        env.update(overrides)
        env.rollback_build = os.path.join(env.deploy_path, buildid)
        if env.autorollback == 'y' or prompt("Rollback to %s? [y/n]" % (
                buildid), default="y", validate="[yn]") == 'y':
            if exists(env.rollback_build):
                run("rm {current_link}".format(**env))
                run("ln -s {rollback_build} {current_link}".format(**env))
                restart_uwsgi()
            else:
                abort("Rollback dir {rollback_build} does not exist".format(
                    **env))



def archive_build():
    if in_dev_mode():
        return
    local(("git archive -o deploy.tgz {gitref}:src".format(**env)))


def put_build_archives():
    if in_dev_mode():
        return
    run("mkdir -p {release_folder}".format(**env))
    put("deploy.tgz", "{release_folder}/deploy.tgz".format(**env))
    put("src/{project}/{environment}_settings.py".format(**env),
        "{release_folder}/prod_settings.py".format(**env))


def create_links():
    if in_dev_mode():
        return
    if is_link(env.previous_link):
        run("rm {previous_link}".format(**env))

    if is_link(env.current_link):
        run("mv {current_link} {previous_link}".format(**env))
    else:
        run("rm -rf {0}".format(env.current_link))

    run("ln -s {release_folder} {current_link}".format(**env))

    if is_link(env.application_link):
        run("rm {application_link}".format(**env))
    run("ln -s {current_link} {application_link}".format(**env))
    run_hooks("post_links")


def tag_build():
    if in_dev_mode():
        return
    if env.new_tag and prompt(
            "Do you wish to tag this build as {new_tag} ?".format(**env)):
        create_new_version_tag()


def create_new_version_tag():
    os.system("git tag {new_tag} {commit_ref}".format(**env))
    tag_link = os.path.join(env.web_root, env.new_tag)
    run("ln -s {0} {1}".format(env.application_link, tag_link))


def get_commit_ref():
    return local("git rev-parse {gitref}".format(**env), capture=True)


def _revert_deploy_links(notify=False):
    print "Attempting to revert to previous version"
    if is_link(env.previous_link):
        run("rm {current_link}".format(**env))
        run("mv {previous_link} {current_link}".format(**env))
        print "Reverted"
    else:
        print "No previous version to use"


def extract_build_archives():
    if in_dev_mode():
        return
    with cd(env.release_folder):
        run("tar xzf deploy.tgz")
        run("rm deploy.tgz")


def cleanup():
    if in_dev_mode():
        return
    local("rm deploy.tgz")
    local("rm -fr build/")


def put_version_txt():
    if in_dev_mode():
        return
    version_file = ""
    if env.new_tag:
        version_file += "Version: %s\n" % env.new_tag
    version_file += ("Date: %s \nCommit: %s\nGitref: %s\nUser:   %s"
                     "\nBuild:  %s\n") % (
        datetime.datetime.isoformat(datetime.datetime.now()),
        env.commit_ref, env.gitref, getpass.getuser(), env.build_folder)
    run('echo "{0}" > {release_folder}/version.txt'.format(version_file,
        **env))


def confirm_settings():
    skip_check = env.get('skip_check', "False") == "True"
    if skip_check:
        return
    print fabsettings.format_env()
    print ""
    if not confirm("Deploy with these settings?"):
        abort("Aborting at user request.")


def migrate_db():

    import fabconfig
    migrate_command = getattr(fabconfig, 'MIGRATE_COMMAND', 'migrate')
    with prefix(env.venv):
        with cd(env.current_link):
            with prefix("export DJANGO_SETTINGS_MODULE={0}".format(
                        env.django_settings)):
                run("{0}/{1}manage.py  {2}".format(
                    env.current_link, env.manage_prefix, migrate_command))


def collect_static():
    with prefix(env.venv):
        with cd(env.current_link):
            with prefix("export DJANGO_SETTINGS_MODULE={0}".format(
                        env.django_settings)):
                run("python {0}/{1}manage.py  "
                    "collectstatic --noinput".format(
                        env.current_link, env.manage_prefix))


def restart_uwsgi():
    if exists('/tmp/%s' % env.project):
        run("touch /tmp/%s" % env.project)
    else:
        print "warning, non graceful reload"
        run("sudo service uwsgi restart")


@task
def info(environment):
    if environment == "vagrant":
        vagrant()
    fabsettings.dev_settings(environment)
    # disabling anoying debug output
    output.update(dict((k, False) for k in output))
    print "Getting info..."
    with cd(env.deploy_path):
        deployments = run("ls -tr").split()
        for dep in sorted(deployments):
            print(" ---- ")
            if is_link(dep):
                print(dep + " -> " + run("readlink %s" % dep))
            else:
                print(dep)
            if exists(os.path.join(dep, "version.txt")):
                print(run("cat {deploy_path}/{0}/version.txt".format(
                    dep, **env)))
            else:
                print("  no version.txt found")
                print ""


@task
def gen_keys(minion_name):

    import fabconfig
    env.hosts = [fabconfig.SALT_HOST]
    sudo('salt-key --gen-keys=%s' % minion_name)
    sudo('cp %s.pub /etc/salt/pki/master/minions/%s' % (
         minion_name, minion_name))
    get('%s.pub' % minion_name)
    get('%s.pem' % minion_name)
    sudo('rm %s.pub' % minion_name)
    sudo('rm %s.pem' % minion_name)


@task
def preseed():
    vagrant()
    minion_name = env.host_string
    import fabconfig
    put('%s/%s.pub' % (fabconfig.SALT_HOST, minion_name))
    put('%s/%s.pem' % (fabconfig.SALT_HOST, minion_name))
    sudo('mkdir -p /etc/salt/pki/minion')
    sudo('mv /home/vagrant/%s.pub '
         '/etc/salt/pki/minion/minion.pub' % minion_name)
    sudo(
        'mv /home/vagrant/%s.pem '
        '/etc/salt/pki/minion/minion.pem' % minion_name)


@task
def postseed():
    import fabconfig
    vagrant()
    sudo('service salt-minion start')
    local('rm -rf %s' % fabconfig.SALT_HOST)


@task
def loaduserkey():
    vagrant()
    import fabconfig
    put('~/.ssh/id_rsa.pub', '/home/vagrant/id_rsa.pub')
    sudo('cat /home/vagrant/id_rsa.pub >> '
         '/home/%s/.ssh/authorized_keys' % fabconfig.DEPLOY_USER)
    sudo('rm /home/vagrant/id_rsa.pub')


@task
def version(environment):
    if environment == "vagrant":
        vagrant()
    fabsettings.dev_settings(environment)
    # disabling anoying debug output
    output.update(dict((k, False) for k in output))
    with cd(env.deploy_path):
        print("current -> " + run("readlink current"))
        if exists("current/version.txt"):
            print(run("cat current/version.txt"))
        else:
            print("  no version.txt found")
            print ""
