from git import Repo


def git_ref(branch):
    repo = Repo(".")
    branch = getattr(repo.heads, branch)
    return branch.commit


def get_username():
    try:
        repo = Repo(".")
        return repo.config_reader().get('user', 'name')
    except:
        print 'Error, git config not found, please set with'
        print '   git config --global user.name "John Doe"'
        raise
