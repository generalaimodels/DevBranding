# Git Comprehensive Guide

---

## Git Basics

**Git** is a distributed version control system designed to handle everything from small to very large projects with speed and efficiency. It tracks changes in source code, enabling multiple developers to collaborate.

- **Repository**: A directory tracked by Git, containing all project files and history.
- **Commit**: A snapshot of changes in the repository.
- **Branch**: A parallel version of the repository, allowing isolated development.

**Key Commands:**
```bash
git --version           # Check installed Git version
git help <command>      # Get help for a specific command
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Repository Initialization

Initialize a new Git repository in a directory.

**Command:**
```bash
git init
```
- Creates a `.git` directory containing all repository metadata.
- Converts an existing project into a Git repository.

---

## Staging and Committing

### Staging

Files must be staged before committing. The staging area allows you to prepare changes.

**Commands:**
```bash
git add <file>          # Stage a specific file
git add .               # Stage all changes in the current directory
git add -A              # Stage all changes (including deletions)
```

### Committing

Commits record staged changes in the repository history.

**Commands:**
```bash
git commit -m "Commit message"      # Commit staged changes with a message
git commit -a -m "Message"          # Stage and commit all tracked files
```

---

## Branching

Branches allow parallel development.

**Commands:**
```bash
git branch                   # List all branches
git branch <branch-name>     # Create a new branch
git checkout <branch-name>   # Switch to a branch
git checkout -b <branch>     # Create and switch to a new branch
git branch -d <branch>       # Delete a branch
```

---

## Merging

Combines changes from one branch into another.

**Commands:**
```bash
git merge <branch>           # Merge specified branch into current branch
```
- Fast-forward merge: Linear history, no merge commit.
- Three-way merge: Non-linear history, creates a merge commit.

---

## Rebasing

Reapplies commits from one branch onto another, creating a linear history.

**Commands:**
```bash
git rebase <branch>          # Rebase current branch onto specified branch
git rebase -i <commit>       # Interactive rebase for editing, squashing, or reordering commits
```
- Use rebase for a cleaner, linear history.
- Avoid rebasing shared branches.

---

## Remote Repositories

Remote repositories are versions of your project hosted on the internet or network.

**Commands:**
```bash
git remote -v                        # List remotes
git remote add origin <url>          # Add a remote repository
git remote remove <name>             # Remove a remote
git remote rename <old> <new>        # Rename a remote
```

---

## Cloning

Creates a local copy of a remote repository.

**Command:**
```bash
git clone <repository-url>
```
- Clones all files, branches, and history.

---

## Pulling and Pushing

### Pulling

Fetches and integrates changes from a remote repository.

**Command:**
```bash
git pull <remote> <branch>
```
- Equivalent to `git fetch` + `git merge`.

### Pushing

Uploads local commits to a remote repository.

**Command:**
```bash
git push <remote> <branch>
```
- Use `git push -u origin <branch>` to set upstream tracking.

---

## Conflict Resolution

Conflicts occur when changes in different branches overlap.

**Steps:**
1. Git marks conflicted files.
2. Edit files to resolve conflicts (look for `<<<<<<<`, `=======`, `>>>>>>>` markers).
3. Stage resolved files:
   ```bash
   git add <file>
   ```
4. Complete the merge or rebase:
   ```bash
   git commit
   # or, if rebasing
   git rebase --continue
   ```

---

## Tagging

Tags mark specific points in history, often for releases.

**Commands:**
```bash
git tag                      # List tags
git tag <tagname>            # Create a lightweight tag
git tag -a <tagname> -m "Message"   # Annotated tag
git show <tagname>           # Show tag details
git push origin <tagname>    # Push a tag to remote
git push origin --tags       # Push all tags
```

---

## Git Log and History

View commit history and details.

**Commands:**
```bash
git log                      # Show commit history
git log --oneline            # Condensed log
git log --graph --all        # Visualize branch structure
git show <commit>            # Show details of a specific commit
```

---

## Diffing

Compare changes between commits, branches, or working directory.

**Commands:**
```bash
git diff                     # Changes not staged
git diff --staged            # Changes staged for commit
git diff <commit1> <commit2> # Differences between commits
git diff <branch1> <branch2> # Differences between branches
```

---

## Resetting and Reverting

### Reset

Moves HEAD and optionally modifies the index and working directory.

**Commands:**
```bash
git reset --soft <commit>    # Move HEAD, keep changes staged
git reset --mixed <commit>   # Move HEAD, unstage changes (default)
git reset --hard <commit>    # Move HEAD, discard all changes
```

### Revert

Creates a new commit that undoes changes from a previous commit.

**Command:**
```bash
git revert <commit>
```
- Safe for shared history.

---

## Stashing

Temporarily saves changes not ready to commit.

**Commands:**
```bash
git stash                    # Stash changes
git stash list               # List stashes
git stash apply [<stash>]    # Apply a stash
git stash pop                # Apply and remove the latest stash
git stash drop <stash>       # Delete a stash
```

---

## Cherry-picking

Apply a specific commit from one branch onto another.

**Command:**
```bash
git cherry-pick <commit>
```
- Useful for applying bug fixes or features selectively.

---

## Submodules

Include external repositories within a repository.

**Commands:**
```bash
git submodule add <repo> <path>    # Add a submodule
git submodule update --init        # Initialize and fetch submodules
git submodule update --remote      # Update submodules to latest commit
git submodule status               # Show submodule status
```

---

## Git Hooks

Scripts that run automatically on certain Git events.

- Located in `.git/hooks/`
- Examples: `pre-commit`, `pre-push`, `commit-msg`

**Usage:**
- Write scripts in shell, Python, etc.
- Make scripts executable.

---

## Git Aliases

Shortcuts for frequently used commands.

**Command:**
```bash
git config --global alias.<alias> '<command>'
```
**Examples:**
```bash
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
```

---

## Git Workflows

Defines how teams use branches and collaborate.

### Common Workflows

- **Centralized Workflow**: Single main branch, all changes committed directly.
- **Feature Branch Workflow**: Each feature in its own branch, merged into main.
- **Gitflow Workflow**: Uses `main`, `develop`, `feature/*`, `release/*`, `hotfix/*` branches.
- **Forking Workflow**: Developers fork the repository, work independently, and submit pull requests.

---

## Git Bisect

Binary search to find the commit that introduced a bug.

**Commands:**
```bash
git bisect start
git bisect bad                # Mark current commit as bad
git bisect good <commit>      # Mark known good commit
# Test and mark each step as good or bad
git bisect good
git bisect bad
git bisect reset              # End bisect session
```
- Efficiently isolates problematic commits.

---

**This guide covers all essential and advanced Git topics, commands, and workflows, ensuring complete understanding and practical proficiency for developers.**