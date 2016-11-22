import os
import fabconfig
import datetime
from fabric.api import local, prompt
from fabric.state import env
from distutils.version import StrictVersion


class RRVersion(StrictVersion):

    def increment(self):
        tmp_version = list(self.version)
        tmp_version[-1] += 1
        self.version = tuple(tmp_version)


def dev_settings(environment):
    env.environment = environment
    env.version = "dev"
    env.new_tag = None
    env.build_folder = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    _global_settings()


def rollback_settings(environment, build_id):
    env.version = build_id
    env.build_folder = "v" + str(env.version)
    env.project = fabconfig.PROJECT
    env.environment = environment
    env.web_root = fabconfig.WEB_ROOT
    env.deploy_path = os.path.join(env.web_root, env.environment)
    env.release_folder = os.path.join(env.deploy_path, env.build_folder)
    env.current_link = os.path.join(env.deploy_path, "current")
    env.manage_prefix = fabconfig.MANAGE_PREFIX
    env.previous_link = os.path.join(env.deploy_path, "previous")


def release_settings(environment, version, gitref):
    env.environment = environment
    env.version = validate_git_version(version, gitref)
    env.new_tag = "v" + str(env.version)
    env.build_folder = "v" + str(env.version)
    _global_settings()


def production_settings(environment, version):
    env.environment = environment
    env.version = version
    env.new_tag = None
    env.build_folder = "v" + str(version)
    _global_settings()


def _global_settings():
    env.autorollback = "prompt"
    env.dev_mode = False
    env.use_ssh_config = True
    env.user = fabconfig.DEPLOY_USER

    env.project = fabconfig.PROJECT
    env.deploy_root = fabconfig.DEPLOY_ROOT
    env.web_root = fabconfig.WEB_ROOT
    env.application_link = os.path.join(env.web_root, "current")
    if hasattr(fabconfig, 'DJANGO_SETTINGS'):
        env.django_settings = fabconfig.DJANGO_SETTINGS
    else:
        env.django_settings = "{0}.settings".format(env.project)
    #env.django_settings = "{0}.{1}_settings".format(
    #    env.project, env.environment)

    env.deploy_path = os.path.join(env.web_root, env.environment)
    env.release_folder = os.path.join(env.deploy_path, env.build_folder)
    env.current_link = os.path.join(env.deploy_path, "current")
    env.manage_prefix = fabconfig.MANAGE_PREFIX
    env.previous_link = os.path.join(env.deploy_path, "previous")
    env.media_files = os.path.join(env.deploy_path, "media_files")
    env.manage_prefix = fabconfig.MANAGE_PREFIX
    env.venv, env.venv_path = _get_venv()


def _get_venv():
    venv_name = '{0}-{1}'.format(env.project, env.environment)
    venv_path = '{0}/.virtualenvs/{1}'.format(env.deploy_root, venv_name)
    return "source {0}/bin/activate".format(venv_path), venv_path


def format_env():
    return """
            hosts:               {hosts}
            environment:         {environment}
            project:             {project}
            gitref:              {gitref}
            commit:              {commit_ref}

            application_link:    {application_link}
            virtual_env:         {venv_path}

            build_folder:        {build_folder}
            new_tag:             {new_tag}
            dev_mode:            {dev_mode}
            version:             {version}
            deploy_path:         {deploy_path}
            release_folder:      {release_folder}
            current_link:        {current_link}
            previous_link:       {previous_link}

            """.format(**env)


def parse_version(tag):
    try:
        return RRVersion(tag.lstrip('v'))
    except:
        return None


def get_latest_git_version():
    tag_str = local("git tag", capture=True)
    tags = tag_str.split('\n') if tag_str else []
    versions = [parse_version(tag) for tag in tags if parse_version(tag)]
    if versions:
        return max(versions)
    else:
        return RRVersion("0.0.1")


def version_to_gitref(version):
    try:
        return local("git rev-parse %s" % version, capture=True)
    except:
        return None


def gitref_to_commit(gitref):
    return version_to_gitref(gitref)


def gitref_to_version(gitref):
    cmd = ("git show-ref --tags -d | grep %s "
           "| sed -e 's,.* refs/tags/,,' -e 's/\^{}//'")
    tags = local(cmd % gitref, capture=True).split()
    tags = [parse_version(x.replace("v", "")) for x in tags if parse_version(
        x.replace("v", ""))]
    if tags:
        return tags[0]
    else:
        return None


def tag_with_version(gitref, version):
    version = "v%s" % str(version)
    r = os.system("git tag %s %s" % (version, gitref))
    if r != 0:
        print "Could not tag with tag %s, perhaps it already exists?" % version
        exit()


def prompt_user_for_version(gitref, version=None):
    version = prompt_version(version)
    tag_with_version(gitref, version)
    return version


def prompt_version(version=None):
    latest_version = get_latest_git_version()
    new_version = get_latest_git_version()
    new_version.increment()
    while True:
        version = prompt(("This release is not currently tagged, "
                         "please provide a version or 'q' to quit"),
                         default=str(new_version))

        if version.strip().lower() == "q":
            exit()
        in_version = version
        version = parse_version(version)
        if not version:
            print"%s is not a  valid version" % in_version
            continue
        if version and version < latest_version and not env.get(
                'hotfix', False):
            yn = prompt(("This version %s is less than the , "
                         "current version %s, a lesser version should only"
                         "be used for a hotfix. continue? (y/n)") % (
                        version, latest_version),
                        default="n")
            if yn.strip().lower() != "y":
                exit()
            return version
        break
    return version


def validate_git_version(version, gitref):
    # conver the gitref to a commit
    # have we been passed a version
    gitref = gitref_to_commit(gitref)
    if version:
        version = parse_version(version)
        if not version:
            raise Exception(
                "The provided version: %s is not a valid version" % version)
        # get the git ref for the version
        version_gitref = version_to_gitref(version)

        # if we have a version
        if version_gitref:
            # and our gitref matches it, then all is well
            if version_gitref == gitref:
                return version
            else:
                # if the version does not match our gitref abort
                raise Exception(
                    ("The provided version %s already exists, but it does not "
                     "match the provided git reference %s. Aborting.") % (
                        version, gitref))
        else:
            # if we have no version, get it from the gitref
            gitref_version = gitref_to_version(gitref)
            if gitref_version:
                raise Exception(
                    ("The provided version %s does not exist, "
                     "but the provided git reference %s already has"
                     " a version %s. Aborting.") % (version,
                                                    gitref, gitref_version))
            else:
                # if there is no version provided, or on the gitref
                # prompt for one
                return prompt_user_for_version(gitref, version)
    else:
        # if we have no version, use the version on the gitref
        version_gitref = gitref_to_version(gitref)
        if version_gitref:
            return version_gitref
        else:
            # if not version on the gitref, ask for one
            return prompt_user_for_version(gitref)
