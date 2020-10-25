from git import Repo 
import os
from shutil import which

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
       
        print(f"Attempting to clone repo: {self}")
        try:
            self.repo = Repo.clone_from(self.remote, self.GetLocalPath(), branch=self.branch)
            print("Successfully cloned repo.")
            return
        except Exception:
            print("Git repo already exists. Error.")
        
        print("Unable to properly configure repository.")

def MakeSymlink(src,dst,overwrite=False):
    exists = os.path.exists(dst)
    if not exists or exists and overwrite:
        os.symlink(src,dst)
        print(f"Created symlink from {src} to {dst}")
    else:
        print(f"Not creating symlink between {src} and {dst}.")

def FindBinaries(deps):
    return { k: which(k) for k,v in deps.items() }

def GetMissingDeps(deps):
    return [k for k,v in deps.items() if v is None]

def main():
    # first, look for binaries
    # if we don't have them, print an error 
    # and tell user to download them
    
    binary_deps = {'cmake': None, 'ccls': None}
    binary_deps = FindBinaries(binary_deps)
    missing_deps = GetMissingDeps(binary_deps)
    if bool(missing_deps):
        print(f"Missing dependencies to configure development environment. Please install: {missing_deps} and try again.")
        return

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

    # symlink vimrc, coc-settings from repo to default search path
    src=os.getcwd()+"/"+vimc.GetLocalPath()
    dst=os.path.expanduser("~")

    MakeSymlink(src+"/vimrc",dst+"/.vimrc")
    MakeSymlink(src+"/coc-settings.json", dst+"/.vim/coc-settings.json")

if __name__ == '__main__':
    main()
