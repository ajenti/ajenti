#!/bin/bash

# build the debian package

dpkg-buildpackage -rfakeroot -tc -sa -us -uc -I".directory" -I".git" -I"buildpackage.sh" -I".crowdin.key" -I"docs" -I"docs_src" -I"tests"
