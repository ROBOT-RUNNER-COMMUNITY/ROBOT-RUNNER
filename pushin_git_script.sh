#!/bin/bash

######################################################################################
# Author : Achraf KHABAR
# Date : 25/04/2025
# Description : This script is used to push changes to a git repository.
# Usage : ./pushin_git_script.sh <branch_name> <commit_message>
# Example : ./pushin_git_script.sh main "My commit message"
#####################################################################################

set -x

# Check if the branch name is provided
if [ -z "$1" ]; then
  echo "Error: Branch name is required."
  echo "Usage: $0 <branch_name> <commit_message>"
  exit 1
fi
# Check if the commit message is provided
if [ -z "$2" ]; then
  echo "Error: Commit message is required."
  echo "Usage: $0 <branch_name> <commit_message>"
  exit 1
fi
# Check if the branch exists
if ! git show-ref --verify --quiet refs/heads/$1; then
  echo "Error: Branch '$1' does not exist."
  exit 1
fi
# Check if the branch is already checked out
if [ "$(git rev-parse --abbrev-ref HEAD)" != "$1" ]; then
  echo "Switching to branch '$1'..."
  git checkout $1
fi
# Check if there are any changes to commit
if [ -z "$(git status --porcelain)" ]; then
  echo "No changes to commit."
  exit 0
fi
# Add all changes to the staging area
git add .
# Commit the changes with the provided commit message
git commit -m "$2"
# Push the changes to the remote repository
git push origin $1
# Check if the push was successful
if [ $? -eq 0 ]; then
  echo "Changes pushed to branch '$1' successfully."
else
  echo "Error: Failed to push changes to branch '$1'."
  exit 1
fi

