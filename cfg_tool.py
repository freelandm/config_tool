from git import Repo
import os

class RepoData:
    def __init__(self, name = None, remote = None, local = 'deps/', branch = 'master'):
        self.name = name
        self.remote = remote
        self.local = local
        self.branch = branch
        self.repo = None
        self.local_path = self.make_path()

    def make_path(self):
        if self.name is not None and self.local is not None:
            slash = '/'
            if self.local.endswith(slash):
                slash = ''
            return self.local + slash + self.name

    def GetLocalPath(self):
        if self.local_path is None:
            self.local_path = self.make_path()
        return self.local_path

    def __str__(self):
        return f'[ Name: {self.name}, Remote: {self.remote}, Local: {self.local_path}, Branch: {self.branch} ]'

    def  BindOrClone(self):
        print("Attempting to bind to local repo: {0}".format(self))
        try:
            self.repo = Repo(self.GetLocalPath())
            print("Successfully bound to repo.")
            return
        except Exception:
            print("Unable to bind to repo. Will attempt to clone repo.")
       
        print("Attempting to clone repo: {0}".format(self))
        try:
            self.repo = Repo.clone_from(self.remote, self.GetLocalPath(), branch=self.branch)
            print("Successfully cloned repo.")
            return
        except Exception:
            print("Git repo already exists. Error.")
        
        print("Unable to properly configure repository.")

def make_symlink(src,dst,overwrite=False):
    exists = os.path.exists(dst)
    if not exists or exists and overwrite:
        os.symlink(src,dst)
        print(f"Created symlink from {src} to {dst}")
    else:
        print(f"Not creating symlink between {src} and {dst}.")

def main():
    # acquire required git repos

    # Vim Configurations repo data
    vimc = RepoData(name='vim_configurations', 
                        remote='https://github.com/freelandm/vim_configurations.git')
    # CCLS repo data
    ccls = RepoData(name='ccls',
                    remote='https://github.com/MaskRay/ccls')

    # BEAR repo data
    bear = RepoData(name='bear',
                    remote='https://github.com/rizsotto/Bear.git')

    # bind to repository
    vimc.BindOrClone()
    ccls.BindOrClone()
    bear.BindOrClone()

    # symlink virc
    src=os.path.expanduser("~")+"/.vimrc"
    dst=os.getcwd()+"/"+vimc.GetLocalPath()+"/vimrc"
    make_symlink(src,dst)
    

if __name__ == '__main__':
    main()
