#! /bin/bash

cd debian
rm -f build/ajenti2_*.deb
cp ../ajenti-core/requirements.txt etc/ajenti/

/usr/local/bin/fpm -s python \
    -t deb \
    --python-bin python3 \
    -p build/ajenti2_VERSION_ARCH.deb \
    -x "*.pyc" \
    -x "*/__pycache__" \
    --no-auto-depends \
    -d build-essential \
    -d python3-pip \
    -d python3-dev \
    -d python3-lxml \
    -d python3-dbus \
    -d python3-augeas \
    -d libssl-dev \
    -d python3-apt \
    -d ntpdate \
    --maintainer arnaud@linuxmuster.net \
    --deb-changelog ../CHANGELOG.txt \
    --config-files etc/ajenti/requirements.txt \
    --after-install scripts/postinstall.sh \
    --deb-systemd systemd/ajenti2.service \
    --deb-systemd-enable \
    --deb-systemd-auto-start \
    ../ajenti-panel

rm -f etc/ajenti/requirements.txt
