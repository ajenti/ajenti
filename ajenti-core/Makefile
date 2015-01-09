PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/ajenti
RPMTOPDIR=$(CURDIR)/build
PROJECT=ajenti
VERSION=`python -c "from ajenti import __version__; print(__version__)"`
PREFIX=/usr
DATE=`date -R`

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
DOCBUILDDIR   = docs/build
DOCSOURCEDIR   = docs/source
ALLSPHINXOPTS   = -d $(DOCBUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) $(DOCSOURCEDIR)

all: resources

resources:
	./compile_resources.py || true

build: resources
	./make_messages.py compile

run:
	./ajenti-panel -v -c ./config.json

doc:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(DOCBUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

cdoc:
	rm -rf $(DOCBUILDDIR)/*
	make doc

tgz: build
	rm dist/*.tar.gz || true
	$(PYTHON) setup.py sdist

upload-tgz: tgz
	$(PYTHON) setup.py sdist bdist_wheel upload

clean:
	$(PYTHON) setup.py clean
	rm -rf $(DOCBUILDDIR)/*
	rm -rf ajenti-1.*
	rm -rf build/ MANIFEST *.egg-info

.PHONY: build resources clean doc cdoc
