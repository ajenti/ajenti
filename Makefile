PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/ajenti
PROJECT=ajenti
VERSION=0.9.0
PREFIX=/usr
DATE=`date -R`

SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
DOCBUILDDIR   = docs/build
DOCSOURCEDIR   = docs/source
ALLSPHINXOPTS   = -d $(DOCBUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) $(DOCSOURCEDIR)

all:

build:
	echo version = \"$(VERSION)\" > ajenti/build.py
	./compile_resources.py 
	
run: 
	./ajenti-panel -v -c ./config.json

doc:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(DOCBUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

cdoc:
	rm -rf $(DOCBUILDDIR)/*
	make doc

install: build
	$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE) --prefix $(PREFIX)

rpm: build
	rm -rf dist/*.rpm
	$(PYTHON) setup.py sdist 
	#$(PYTHON) setup.py bdist_rpm --spec-file dist/ajenti.spec #--post-install=rpm/postinstall --pre-uninstall=rpm/preuninstall
	cat dist/ajenti.spec.in | sed s/__VERSION__/$(VERSION)/g > ajenti.spec
	rpmbuild -bb ajenti.spec --buildroot .
	rm ajenti.spec
	mv ~/rpmbuild/RPMS/noarch/$(PROJECT)*.rpm dist

deb: build
	cat debian/changelog.in | sed s/__VERSION__/$(VERSION)/g | sed "s/__DATE__/$(DATE)/g" > debian/changelog

	rm -rf dist/*.deb
	$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=../
	rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
	dpkg-buildpackage -b -rfakeroot -us -uc

	mv ../$(PROJECT)*.deb dist/
	
	rm ../$(PROJECT)*.orig.tar.gz
	rm ../$(PROJECT)*.changes
	rm debian/changelog

upload-deb: deb
	scp dist/*.deb root@ajenti.org:/srv/repo
	ssh root@ajenti.org /srv/repo/rebuild-debian.sh

tgz: build
	rm dist/*.tar.gz || true
	$(PYTHON) setup.py sdist 

clean:
	$(PYTHON) setup.py clean
	rm -rf $(DOCBUILDDIR)/*
	rm -rf build/ debian/$(PROJECT)* debian/*stamp* debian/files MANIFEST *.egg-info
	find . -name '*.pyc' -delete
	find . -name '*.c.js' -delete
	find . -name '*.coffee.js' -delete
	find . -name '*.c.css' -delete
	find . -name '*.less.css' -delete
