#! /bin/bash

do_fpm () {
	/usr/local/bin/fpm -s python --log debug \
	    -t deb \
	    --python-bin python3 \
	    -p debian/build/ajenti_plugin_$1_VERSION_ARCH.deb \
	    -x "*.pyc" \
	    -x "*/__pycache__" \
	    --no-auto-depends \
	    --maintainer arnaud@linuxmuster.net \
	    --deb-changelog CHANGELOG.txt \
	    /tmp/testbuild
}

rm -f debian/build/ajenti_plugin_*

## Core package
do_fpm core

## Dashboard package
#do_fpm dashboard
