from git import Repo 
import os
from shutil import which
import wget
import tarfile
import subprocess
import csv

gMinVimVersion = 8.3
gMinNodeVersion = 10.12

class RepoData:
    def __init__(self, name = None, remote = None, local = 'deps/', branch = 'master'):
        self.name = name
        self.remote = remote
        self.local = local
        self.branch = branch
        self.repo = None
        self.local_path = self.make_path()

    #internal method
    def make_path(self):
        if self.name is not None and self.local is not None:
            slash = '/'
            if self.local.endswith(slash):
                slash = ''
            if not os.path.exists(self.local):
                os.mkdir(self.local)
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

def FindBinary(prg):
    return which(prg)

def GetMissingDeps(deps):
    return [k for k,v in deps.items() if v is None]

def GetVimVersion(vimb):
    # need to get the output here...
    process = subprocess.Popen([vimb, "--version"], stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    reader = csv.DictReader(stdout.decode('ascii').splitlines(), delimiter=' ', skipinitialspace=True, fieldnames=['VIM', 'dash', 'Vi', 'IMproved', 'version', 'remainder'])
    index = 0
    row_dict = {}
    while index < 1:
        for row in reader:
            row_dict = row
            index += 1
            break
    return float(row_dict['version'])

def GetNodeVersion(nodeb):
    output = subprocess.getoutput(nodeb+" --version")
    vlist = output.split('v')[1].split('.')
    version = float(vlist[0]+'.'+vlist[1])
    return version

def PrepareDeps():
    ccls = 'ccls'
    bear = 'bear'
    vim = 'vim'
    node = 'node'
    deps = {ccls:None, bear:None, vim:None, node:None}
    missing_deps = []
    deps[ccls] = FindBinary(ccls)
    deps[vim] = FindBinary(vim)
    deps[node] = FindBinary(node)
    if deps[ccls] is None:
        missing_deps.append(ccls)
        cmake = 'cmake'
        deps[cmake] = FindBinary(cmake)
        if deps[cmake] is None:
            missing_deps.append(cmake)
    if deps[vim] is None or GetVimVersion(deps[vim]) < gMinVimVersion:
        if deps[vim] is not None:
            print(min_version_error_log(vim, deps[vim], GetVimVersion(deps[vim]), gMinVimVersion))
        else:
            print("Vim binary not found.")
        missing_deps.append(vim)
    if deps[node] is None or GetNodeVersion(deps[node]) < gMinNodeVersion:
        if deps[node] is not None:
            print(min_version_error_log(node, deps[node], GetNodeVersion(deps[node]), gMinNodeVersion))
        else:
            print("Node binary not found. Try running {} to install Node.".format('curl -sL install-node.now.sh/lts | bash'))
        missing_deps.append(node)
    

    return deps, missing_deps

def InstallCmake():
    print("No access to 'yum' package via python. To install 'cmake' manually, please run 'yum install cmake'.")
    return False

def InstallCcls():
    # CCLS repo data
    ccls = RepoData(name='ccls',
                    remote='https://github.com/MaskRay/ccls')
    ccls.BindOrClone()
    cmake = 'cmake'
    cmakeb = FindBinary(cmake)
    os.chdir(ccls.GetLocalPath())
    


def InstallVim8():
    return False

def InstallBear():
    return False

def install_failure_log(name):
    return f'Failed to install {name}. Unable to proceed. Please manually install {name} and try again.'

def min_version_error_log(name, path, insv, minv):
    return f'{name} version is too low. Current version installed at {path} has version {insv}. Minimum supported version is {minv}'

def InstallDeps(missing_deps):
    success = True

    if 'cmake' in missing_deps:
        if not InstallCmake():
            print(install_failure_log('cmake'))
            success = False

    if 'ccls' in missing_deps:
        if 'cmake' not in missing_deps:
            if not InstallCcls():
                print(install_failure_log('ccls'))
                success = False
        else:
            print('Missing cmake. Will not try to install ccls.')

    if 'vim' in missing_deps:
        if not InstallVim8():
            print(install_failure_log('vim'))
            success = False

    if 'bear' in missing_deps:
        if not InstallBear():
            print(install_failure_log('bear'))
            success = False

    return success


def main():

    # with argparser, we can provide a path for downloaded binaries

    deps, missing_deps = PrepareDeps()
    print(f'Deps: {deps}, missing_deps: {missing_deps}')
    if not InstallDeps(missing_deps):
        print("Failed to install dependencies. Bailing out.")
        return

    # Vim Configurations repo data
    vimc = RepoData(name='vim_configurations', 
                        remote='https://github.com/freelandm/vim_configurations.git')

    # the following should be under the hood of install dependencies.
    # BEAR repo data
    bear = RepoData(name='bear',
                    remote='https://github.com/rizsotto/Bear.git')

    # bind to repository
    vimc.BindOrClone()
    bear.BindOrClone()

    # symlink vimrc, coc-settings from repo to default search path
    src=os.getcwd()+"/"+vimc.GetLocalPath()
    dst=os.path.expanduser("~")

    MakeSymlink(src+"/vimrc",dst+"/.vimrc")
    MakeSymlink(src+"/coc-settings.json", dst+"/.vim/coc-settings.json")

if __name__ == '__main__':
    main()
