# Git – End-to-End Technical Reference  

---

## Table of Contents
1. Git Basics  
2. Repository Initialization  
3. Staging and Committing  
4. Branching  
5. Merging  
6. Rebasing  
7. Remote Repositories  
8. Cloning  
9. Pulling and Pushing  
10. Conflict Resolution  
11. Tagging  
12. Git Log & History  
13. Diffing  
14. Resetting & Reverting  
15. Stashing  
16. Cherry-picking  
17. Submodules  
18. Git Hooks  
19. Git Aliases  
20. Git Workflows  
21. Git Bisect  

---

## 1. Git Basics
### Core Concepts
- **Snapshot-based VCS**: Git stores snapshots, not diffs.  
- **Repository (repo)**: `.git/` directory tracking complete history.  
- **Three trees**:  
  - **Working Directory** – current files.  
  - **Index/Stage** – files prepped for next commit.  
  - **HEAD** – last commit checkout.  
- **SHA-1 / SHA-256**: Immutable object IDs (2.42+ may use SHA-256).  

### Essential Commands
```bash
git init           # create repo
git status         # current state
git add <file>     # stage file
git commit -m "…"  # save snapshot
git log --oneline  # history
```

### Configuration
```bash
git config --global user.name  "Ada Lovelace"
git config --global user.email "ada@lovelace.dev"
git config --global init.defaultBranch main   # default branch name
git config --global core.editor "nvim"        # editor
```

---

## 2. Repository Initialization
### Local Init
```bash
git init [--bare] [<path>]
```
- `--bare`: for server-side repos (no working tree).  
- Creates `.git/` with sub-directories: `objects/`, `refs/`, `hooks/`, etc.

### Cloning as Initialization
```bash
git clone <url> [<dir>] [--bare] [--mirror]
```
- `--mirror`: bare + fetch all refs, incl. notes, reflogs.

---

## 3. Staging and Committing
### Staging (Index)
```bash
git add <file|dir|pattern>
git add -p               # interactive hunks
git reset <file>         # unstage specific paths
```
### Committing
```bash
git commit -m "subject"                # normal
git commit -a -m "msg"                 # add tracked changes + commit
git commit --amend                     # rewrite last commit
GIT_EDITOR=vim git commit              # open editor for full message
```
Best Practices  
- Imperative, 50-char subject, blank line, 72-char body wrap.  
- Use `--signoff` for DCO; `-S` for GPG signature.

---

## 4. Branching
### Creating & Switching
```bash
git branch feature/login
git switch feature/login     # or: git checkout -b feature/login
```
### Listing
```bash
git branch -a    # local + remote
git branch -vv   # SHA + upstream
```
### Deleting
```bash
git branch -d <branch>   # only if fully merged
git branch -D <branch>   # force delete
```
Internals: branches are lightweight refs in `.git/refs/heads/`.

---

## 5. Merging
### Fast-Forward vs Non-FF
```bash
git merge <branch>                # auto fast-forward if possible
git merge --no-ff <branch>        # create explicit merge commit
```
### Strategies
- `recursive` (default)  
- `ours`, `theirs`, `octopus`, `subtree`

### Options
```bash
git merge --squash <branch>       # compress into single commit (no merge)
git merge --abort                 # stop & reset during conflict
```

---

## 6. Rebasing
### Basic Rebase
```bash
git rebase <upstream> [branch]
```
- Moves branch commits to new base; replays in order.

### Interactive
```bash
git rebase -i <upstream>
# pick, reword, edit, squash, fixup, exec, drop
```
### Workflow Tips
- Never rebase published history (unless collaborators consent).  
- Use `--rebase` flag on pulls to keep linear history.

---

## 7. Remote Repositories
### Adding & Managing
```bash
git remote add origin git@github.com:org/repo.git
git remote -v
git remote rename origin upstream
git remote remove upstream
```
### Fetching
```bash
git fetch [--all] [--prune] [<remote>]
```
- `prune` deletes local refs that vanished on remote.

---

## 8. Cloning
```bash
git clone <url> [--branch <name>] [--depth <N>] [--filter=blob:none]
```
- Shallow clone (`--depth`) speeds CI.  
- Partial clone (`--filter`) avoids large blobs.

---

## 9. Pulling and Pushing
### Pull
```bash
git pull [--rebase] [<remote> [<branch>]]
```
- Behind the scenes: `git fetch` + `git merge` (or rebase).

### Push
```bash
git push <remote> <branch>
git push -u origin feature/login   # set upstream
git push --force-with-lease        # safe force push
git push --tags                    # send tags
```
Best Practices  
- Protect main branches on server; require PRs/MRs.  
- Prefer `--force-with-lease` over `--force`.

---

## 10. Conflict Resolution
### Identifying
```bash
<<<<<<< HEAD
…your changes…
=======
…incoming changes…
>>>>>>> feature
```
### Tools
```bash
git mergetool                   # launches configured GUI/CLI
git diff --name-only --diff-filter=U  # list conflicted files
```
### Steps
1. Open each conflicted file; decide final lines.  
2. `git add <file>` after resolution.  
3. `git merge --continue` or `git rebase --continue`.  
4. Test build.  

---

## 11. Tagging
### Lightweight vs Annotated
```bash
git tag v1.2.0            # lightweight
git tag -a v1.2.0 -m "Rls 1.2"    # annotated + message + signature possible
```
### Pushing Tags
```bash
git push origin v1.2.0
git push origin --tags    # all tags
```
### Deleting / Moving
```bash
git tag -d v1.2.0
git push origin :refs/tags/v1.2.0    # remove on remote
```

---

## 12. Git Log & History
### Basic Views
```bash
git log
git log --oneline --graph --decorate --all
git log --since="2 weeks ago" --author="Ada"
```
### Formatting
```bash
git log --pretty=format:"%h %ad | %s%d [%an]" --date=short
```
### File History
```bash
git log --follow -- <file>
```

---

## 13. Diffing
```bash
git diff                # unstaged vs working tree
git diff --staged       # staged vs HEAD
git diff HEAD~3..HEAD   # range
git diff --stat         # summary
git difftool            # external viewer
```
Binary & Word Diffs  
```bash
git diff --word-diff
git diff --binary
```

---

## 14. Resetting & Reverting
### git reset
```bash
git reset --soft HEAD~1   # move HEAD, keep index & WD
git reset --mixed HEAD~1  # default; reset index
git reset --hard HEAD~1   # nuke index + WD
```
### git revert
```bash
git revert <commit>       # create new commit to undo
git revert --no-commit <range>   # batch revert
```
Use reset for *local* rewrites; revert for *public* history.

---

## 15. Stashing
### Basic Usage
```bash
git stash push -m "wip: bugfix"
git stash list
git stash show -p stash@{2}
git stash apply stash@{2}
git stash drop stash@{2}
git stash pop            # apply + drop latest
```
### Advanced
- `git stash push -p` interactively select hunks.  
- `git stash branch hotfix stash@{1}` create branch from stash.

---

## 16. Cherry-picking
```bash
git cherry-pick <commitSHA>
git cherry-pick A..B         # pick range (excludes A)
git cherry-pick --edit
git cherry-pick --skip       # while resolving conflicts
```
Conflict resolution identical to merge/rebase flow.

---

## 17. Submodules
### Adding
```bash
git submodule add <url> path/to/dir
git commit -m "Add submodule x"
```
### Cloning with Submodules
```bash
git clone --recurse-submodules <url>
```
### Updating
```bash
git submodule update --remote --merge
```
Maintenance Tips  
- Treat submodule pointers as version locks.  
- CI: run `git submodule sync --recursive`.

---

## 18. Git Hooks
### Location
- `.git/hooks/` (local) or use *core.hooksPath* for repo-level sharing.

### Common Hooks
- `pre-commit`: lint/tests.  
- `prepare-commit-msg`: template injection.  
- `commit-msg`: enforce message format or GPG.  
- `pre-push`: CI, static analysis.  
- `post-receive`: server-side deployment trigger.

### Enabling
Hooks are plain executables (bash, python, etc.) without extension; give `chmod +x`.

---

## 19. Git Aliases
### Defining
```bash
git config --global alias.lg "log --oneline --graph --decorate --all"
git config --global alias.co "checkout"
git config --global alias.st "status -sb"
```
### Complex Aliases via !sh
```bash
git config alias.cleanup '!f() { git branch --merged | grep -vE "(^\*|main|dev)" | xargs -r git branch -d; }; f'
```

---

## 20. Git Workflows
### Centralized
- Single main branch, developers pull/commit directly.

### Feature Branch / GitHub Flow
1. Branch off `main` (`feature/x`).  
2. PR → review → merge via squash/rebase → delete branch.

### Git Flow (Vincent Driessen)
- `main` (production), `develop`, feature, release, hotfix.  
- Heavy; suited for versioned releases.

### Trunk Based
- Short-lived branches (<24h) to `main`.  
- Use feature flags; CI/CD mandatory.

### Forking
- External contributors fork repo; create PRs from fork.

---

## 21. Git Bisect
### Purpose
Binary search to find first bad commit.
```bash
git bisect start
git bisect bad                # current rev is failing
git bisect good v1.1.0        # known good tag
```
Git checks out midpoint; run tests:

```bash
./run_tests.sh && git bisect good || git bisect bad
```
After isolation:
```bash
git bisect reset              # return to original HEAD
```
Automate:
```bash
git bisect run ./test_script.sh
```

---

### Quick Reference Cheat-Sheet
```bash
Status            : git status -sb
Stage             : git add -p
Undo Stage        : git restore --staged <f>
Undo WD change    : git restore <f>
Branch list       : git branch -a
Create + switch   : git switch -c <b>
Merge             : git merge --no-ff <b>
Rebase            : git rebase -i <up>
Log pretty        : git lg        # alias
Diff cached       : git diff --staged
Reset soft        : git reset --soft HEAD~1
Stash             : git stash push -m "msg"
Cherry-pick       : git cherry-pick <sha>
Bisect            : git bisect start/bad/good
```

---

### Recommended Global Config Snippet
```bash
git config --global core.autocrlf input
git config --global pull.rebase true
git config --global fetch.prune true
git config --global rerere.enabled true
git config --global merge.ff only
git config --global diff.colorMoved zebra
```

---

Developers now possess an exhaustive command-level and conceptual mastery of Git.