# Git Setup

## Cloning the Project to Your Machine

- you must have git set up on your machine
- have your account set up
- in your terminal go to the directory you want to be working in
- run `https://github.com/justindal/3005-Final-Project-V1.git`

## Initial Project Setup

- cd into the repo
- in the top level of the repo clone the data we are working with:
  `git clone https://github.com/statsbomb/open-data.git`
- once finished cloning, cd into the open-data folder:
  `cd open-data`
- switch to the specific branch the course is using:
  `git checkout 0067cae166a56aa80b2ef18f61e16158d6a7359a`
- cd back to the top level of the repo: `cd`

## New Commits

a commit is a change in git. when you make a new change, you create a new commit and push it to the main branch of the project.

1. go to the main branch `git checkout main`
2. pull latest changes from repo `git reset --hard origin/main`. this will remove any local changes, make sure you do this before making changes.
3. create a new branch for your changes: `git checkout -b <branch-name>`. for example a branch could be called `updated-query1`
4. make your changes
5. add your changes `git add .`
6. add a commit message: `git commit -m "<commit-message>"`
7. while you were working on your changes, other people may have pushed changes to the remote repository; you must pull the latest changes from the remote repository by running `git pull --rebase origin main`. this merges latest changes from the remote repository into your branch.
8. Push your changes to the remote repository by running `git push --set-upstream remote <branch>`. Replace `<branch>` with the name of the branch you created.
9. once changes are pushed, view the github page, and create a pull request to merge the changes into the main branch [github link](https://github.com/justindal/3005-Final-Project-V1)
