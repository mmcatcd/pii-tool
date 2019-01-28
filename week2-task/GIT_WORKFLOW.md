# Git Workflow

A Git workflow is very important to insure that developers can collaborate in a way that doesn't affect other developers work on the team and to maximise project organisation.

## Architecture

| Branch | Description |
|--------|-------------|
| master | This is where production ready code will lie. Development code will slowly get merged into the master as it becomes production ready.
| dev    | This is where all development code will reside. If developers wish to implement a new feature, they will create their own branch off this. |
| [devname]-[feature] | This is the naming convention for a developer who wishes to implement a new feature for the project. They must create a new branch off `dev` with their name followed by the name of the feature they are implementing.

## Protocol

As mentioned in the table above, if a developer wishes to begin implementing a new feature in the project they must:

1. Create a **Projects** item for the feature and move it into the **Development** section of the board.
2. Create a branch off the `dev` branch with your name followed by the name of the feature as the title.
3. Commit all changes to the new branch you created.
4. When the feature has been finished, create a **pull request** back into the `dev` branch. This pull request should be reviewed by another developer and either accepted or declined if more work must be done to the feature before it can be merged.

## What is a Branch?

<img src="./resources/01.svg">

Branching is a very powerful tool in git that allows developers to create an isolated line of development that can be worked on until a feature is implemented and can then be merged back into the original branch.

### Create a new Branch

1. Checkout the branch you wish to branch off. You can list all local branches by:

```
$ git branch
```

You can list all remote branches:

```
$ git branch --remote
```

You can checkout a branch:

```
$ git checkout [branch name]
```

2. Create a new branch:

```
$ git checkout -b [nameofnewbranch]
```

It should switch to the new branch for you. You can now commit, push and pull from the repo as you would in the master branch.

## What are Pull Requests?

Pull Requests are a feature given in GitHub's git repo's. They allow a developer to create a request to merge some work they've completed on another branch into the original branch. This is useful because the request can be reviewed by other teams members and they can then decide whether the code should be merged or not.

Pull Requests are a very important part of the development process because they force peer-based code reviews.

### Create a Pull Request

1. Go to the *Pull Request* tab on the [GitHub repo page](https://github.com/mmcatcd/sweng-group-20) and press **New pull request**.
2. Select the base branch and the compare branch. The compare branch is the branch you want to merge into the base.
3. Write a small description about the feature and why you want to merge it.
4. Press **Create pull request** button.

### Reviewing a Pull Request

1. Go to the *Pull Request* tab on the [GitHub repo page](https://github.com/mmcatcd/sweng-group-20) and look at the list of open pull requests.
2. Select the pull request you wish to review.
3. You can check the commits made with diffs of the changes and new files the developer added to the branch. Review the code.
4. If you are happy with the code, press the **Merge pull request** button.
5. If you are not happy with the code, leave a comment and close the pull request.