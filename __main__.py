#!/usr/bin/env python3
import sys

from ADService import ADService

args = sys.argv

if len(args) != 3:
    print('Launch as: python __main__.py ${ghprbActualCommit} ${ghprbPullId}')
    exit(0)

git_commit = args[1]
git_pull_request = args[2]

service = ADService()
service.analyze(git_commit, git_pull_request)
