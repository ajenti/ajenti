#!/bin/bash
rm -r sandbox/*
find | grep '.pyc' | xargs rm
git add .
git add -u .
git commit
git push origin master


