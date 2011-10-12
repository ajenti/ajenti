PYTHON=`which python`
DESTDIR=/
BUILDIR=$(CURDIR)/debian/ajenti
PROJECT=ajenti
VERSION=0.5.0


SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
DOCBUILDDIR   = docs/build
DOCSOURCEDIR   = docs/source
ALLSPHINXOPTS   = -d $(DOCBUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) $(DOCSOURCEDIR)

doc:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(DOCBUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

cdoc:
	rm -rf $(DOCBUILDDIR)/*
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(DOCBUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."


source:
		$(PYTHON) setup.py sdist $(COMPILE)

install:
		$(PYTHON) setup.py install --root $(DESTDIR) $(COMPILE)

buildrpm:
		$(PYTHON) setup.py bdist_rpm --spec-file dist/ajenti.spec #--post-install=rpm/postinstall --pre-uninstall=rpm/preuninstall

builddeb:
		# build the source package in the parent directory
		# then rename it to project_version.orig.tar.gz
		$(PYTHON) setup.py sdist $(COMPILE) --dist-dir=../
		rename -f 's/$(PROJECT)-(.*)\.tar\.gz/$(PROJECT)_$$1\.orig\.tar\.gz/' ../*
		# build the package
		dpkg-buildpackage -i -I -rfakeroot

clean:
		$(PYTHON) setup.py clean
		rm -rf $(DOCBUILDDIR)/*
		$(MAKE) -f $(CURDIR)/debian/rules clean
		rm -rf build/ MANIFEST dist Ajenti.egg-info
		find . -name '*.pyc' -delete
