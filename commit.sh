#!/bin/bash
find | grep '.pyc' | xargs rm
git add .
git add -u .
git commit
git push origin master


