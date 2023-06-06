# Secret Scanning

Gitleaks is a SAST tool for **detecting** and **preventing** hardcoded secrets like passwords, api keys, and tokens in git repos. Gitleaks is an **easy-to-use, all-in-one solution** for detecting secrets, past or present, in your code.

# Setup GitLeaks

Gitleaks can be installed using Homebrew, Docker, or Go. Gitleaks is also available in binary form for many popular platforms and OS types on the [releases page](https://github.com/zricethezav/gitleaks/releases). In addition, Gitleaks can be implemented as a pre-commit hook directly in your repo or as a GitHub action using [Gitleaks-Action](https://github.com/gitleaks/gitleaks-action).
## Installing
### Windows
Download gitleaks locally from [here](https://github.com/gitleaks/gitleaks) for secret scanning. After downloading, add path of the *gitleaks.exe* to system environment variables so that you can use the *gitleaks* command in command prompt and windows shell.
### Other Operating Systems
```
# MacOS
brew install gitleaks

# Docker (DockerHub)
docker pull zricethezav/gitleaks:latest
docker run -v ${path_to_host_folder_to_scan}:/path zricethezav/gitleaks:latest [COMMAND] --source="/path" [OPTIONS]

# Docker (ghcr.io)
docker pull ghcr.io/gitleaks/gitleaks:latest
docker run -v ${path_to_host_folder_to_scan}:/path gitleaks/gitleaks:latest [COMMAND] --source="/path" [OPTIONS]

# From Source
git clone https://github.com/gitleaks/gitleaks.git
cd gitleaks
make build
```
## Usage
```
Usage:
  gitleaks [command]

Available Commands:
  completion  generate the autocompletion script for the specified shell
  detect      detect secrets in code
  help        Help about any command
  protect     protect secrets in code
  version     display gitleaks version

Flags:
  -b, --baseline-path string       path to baseline with issues that can be ignored
  -c, --config string              config file path
                                   order of precedence:
                                   1. --config/-c
                                   2. env var GITLEAKS_CONFIG
                                   3. (--source/-s)/.gitleaks.toml
                                   If none of the three options are used, then gitleaks will use the default config
      --exit-code int              exit code when leaks have been encountered (default 1)
  -h, --help                       help for gitleaks
  -l, --log-level string           log level (trace, debug, info, warn, error, fatal) (default "info")
      --max-target-megabytes int   files larger than this will be skipped
      --no-color                   turn off color for verbose output
      --no-banner                  suppress banner
      --redact                     redact secrets from logs and stdout
  -f, --report-format string       output format (json, csv, sarif) (default "json")
  -r, --report-path string         report file
  -s, --source string              path to source (default ".")
  -v, --verbose                    show verbose output from scan

Use "gitleaks [command] --help" for more information about a command.
```
## Commands
There are two commands you will use to detect secrets;  `detect`  and  `protect`.

#### [](https://github.com/gitleaks/gitleaks#detect)Detect

The  `detect`  command is used to scan repos, directories, and files. This command can be used on developer machines and in CI environments.

When running  `detect`  on a git repository, gitleaks will parse the output of a  `git log -p`  command (you can see how this executed  [here](https://github.com/zricethezav/gitleaks/blob/7240e16769b92d2a1b137c17d6bf9d55a8562899/git/git.go#L17-L25)).  [`git log -p`  generates patches](https://git-scm.com/docs/git-log#_generating_patch_text_with_p)  which gitleaks will use to detect secrets. You can configure what commits  `git log`  will range over by using the  `--log-opts`  flag.  `--log-opts`  accepts any option for  `git log -p`. For example, if you wanted to run gitleaks on a range of commits you could use the following command:  `gitleaks detect --source . --log-opts="--all commitA..commitB"`. See the  `git log`  [documentation](https://git-scm.com/docs/git-log)  for more information.

You can scan files and directories by using the  `--no-git`  option.

#### [](https://github.com/gitleaks/gitleaks#protect)Protect

The  `protect`  command is used to scan uncommitted changes in a git repo. This command should be used on developer machines in accordance with  [shifting left on security](https://cloud.google.com/architecture/devops/devops-tech-shifting-left-on-security). When running  `protect`  on a git repository, gitleaks will parse the output of a  `git diff`  command (you can see how this executed  [here](https://github.com/zricethezav/gitleaks/blob/7240e16769b92d2a1b137c17d6bf9d55a8562899/git/git.go#L48-L49)). You can set the  `--staged`  flag to check for changes in commits that have been  `git add`ed. The  `--staged`  flag should be used when running Gitleaks as a pre-commit.

**NOTE**: the  `protect`  command can only be used on git repos, running  `protect`  on files or directories will result in an error message.
# Setup Precommit
Git hook scripts are useful for identifying simple issues before submission to code review. We run our hooks on every commit to automatically point out issues in code such as missing semicolons, trailing whitespace, and debug statements. By pointing these issues out before code review, this allows a code reviewer to focus on the architecture of a change while not wasting time with trivial style nitpicks.
## Installation

Before you can run hooks, you need to have the pre-commit package manager installed.

Using pip:
```
pip  install  pre-commit
```
In a python project, add the following to your requirements.txt (or requirements-dev.txt):
```
pre-commit
```
As a 0-dependency  [zipapp](https://docs.python.org/3/library/zipapp.html):

-   locate and download the  `.pyz`  file from the  [github releases](https://github.com/pre-commit/pre-commit/releases)
-   run  `python pre-commit-#.#.#.pyz ...`  in place of  `pre-commit ...`

Using  [homebrew](https://brew.sh/):
```
brew  install  pre-commit
```
Using  [conda](https://conda.io/)  (via  [conda-forge](https://conda-forge.org/)):
```
conda  install  -c  conda-forge  pre-commit
```
## Quick start  [¶](https://pre-commit.com/#quick-start)

### 1. Install pre-commit

-   follow the  [install](https://pre-commit.com/#install)  instructions above
-   `pre-commit --version`  should show you what version you're using
```
$ pre-commit --version
pre-commit 3.3.2
```
### 2. Add a pre-commit configuration

-   create a file named  `.pre-commit-config.yaml`
-   you can generate a very basic configuration using  [`pre-commit sample-config`](https://pre-commit.com/#pre-commit-sample-config)
-   the full set of options for the configuration are listed  [below](https://pre-commit.com/#plugins)
-   this example uses a formatter for python code, however  `pre-commit`  works for any programming language
-   other  [supported hooks](https://pre-commit.com/hooks.html)  are available
```
repos:
-  repo:  https://github.com/pre-commit/pre-commit-hooks
  rev:  v2.3.0
  hooks:
  -  id:  check-yaml
  -  id:  end-of-file-fixer
  -  id:  trailing-whitespace
-  repo:  https://github.com/psf/black
  rev:  22.10.0
  hooks:
  -  id:  black
```
### 3. Install the git hook scripts

-   run  `pre-commit install`  to set up the git hook scripts
```
$ pre-commit  install
pre-commit installed at .git/hooks/pre-commit
```
-   now  `pre-commit`  will run automatically on  `git commit`!

### 4. (optional) Run against all the files

-   it's usually a good idea to run the hooks against all of the files when adding new hooks (usually  `pre-commit`  will only run on the changed files during git hooks)
```
$ pre-commit run --all-files
[INFO] Initializing environment for https://github.com/pre-commit/pre-commit-hooks.
[INFO] Initializing environment for https://github.com/psf/black.
[INFO] Installing environment for https://github.com/pre-commit/pre-commit-hooks.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
[INFO] Installing environment for https://github.com/psf/black.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
Check Yaml...............................................................Passed
Fix End of Files.........................................................Passed
Trim Trailing Whitespace.................................................Failed
- hook id: trailing-whitespace
- exit code: 1

Files were modified by this hook. Additional output:

Fixing sample.py

black....................................................................Passed
```
-   oops! looks like I had some trailing whitespace
-   consider running that in  [CI](https://pre-commit.com/#usage-in-continuous-integration)  too
# Test Secret Scanning
To test the secret scanning look at the following test below
## Prerequisites

GitLeaks: you need to install the gitleaks locally

Precommit: you need to install the precommit cli

## Setup

1.  Run the command “pre-commit install”
    

## Steps

1.  To test change the code
    
2.  If you want to test it for failure cases, add a hardcoded key or secret
    
3.  Commit the changes
    

## Criteria

4.  If you added secrets, commit should fail
    
5.  If you did not add any secret, commit should succeed
    

# Test for Gitleaks Github Action

## Steps

1.  To test change the code
    
2.  If you want to test it for failure cases, add a hardcoded key or secret
    
3.  Commit the changes/ Create a PR (pull request)
    

## Criteria

4.  Gitleaks github action should run on github and succeed, if you did not add any secrets
    
5.  If you added any secret, Gitleaks github action should run on github and fail