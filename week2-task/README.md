# Week 2 Task - GitHub Tutorial

## Task

1. Clone the repo by typing `git clone https://[ldapuname]@github.com/mmcatcd/sweng-group-20.git`.
1. Create a new branch with your **LDAP** username.
2. Add a file to the branch called `[ldapusername].txt` and commit it to the new branch you created.
3. Remove the file from the branch and commit the file removal.
4. Create a pull request to merge the new branch you created into master.

## More Information

Check out the `GIT_WORKFLOW.md` file for more information about branching and merging.

## Useful Tools

### Cloning

#### Unix or Linux

Git comes preinstalled on most Unix and Linux systems. To clone a repo open a new **terminal** window and type:

```
$ git clone [url for the git repo]
$ cd [reponame]
```

#### Windows

I would recommend installing the [Git command line for Windows](https://git-scm.com/download/win). You can then use the `git clone` command as in Unix and Linux to clone a repo.

### Check Status

To check is there is any staged or unstaged changes for committing type:

```
$ git status
```

### Committing

1. Add the files you wish to commit. If you wish to commit all unstaged changes, type:

```
$ git add -A
```

Otherwise type:

```
$ git add paths/of/ files/to/add
```

2. Commit to local repo.

```
$ git commit -m "Add a meaningful comment about the changes you made."
```

3. Push the changes to the remote repo.

```
$ git push origin [current branch. master by default]
```

### Pulling the most up-to-date repo

```
$ git pull
```