## Flag for custom config file
CONFIGFILE := ''

all: build

build:
	ajenti-dev-multitool --msgfmt
	ajenti-dev-multitool --build-frontend

run:
	cd ajenti-panel && ./ajenti-panel -v --autologin --plugins ../plugins-new $(CONFIGFILE)

rundev:
	cd ajenti-panel && ./ajenti-panel -v --autologin --plugins ../plugins-new --dev $(CONFIGFILE)

rundevlogin:
	cd ajenti-panel && ./ajenti-panel -v --plugins ../plugins-new --dev $(CONFIGFILE)

runprod:
	cd ajenti-panel && ./ajenti-panel --plugins ../plugins-new $(CONFIGFILE)

rund:
	cd ajenti-panel && ./ajenti-panel --plugins ../plugins-new -d $(CONFIGFILE)

clean:
	find | grep \.pyc | xargs rm || true
	rm -rf plugins-new/*/dist || true
	rm -rf plugins-new/*/frontend/node_modules || true
	rm -rf plugins-new/*/.last-upload || true


doc:
	sphinx-build -b html -d docs/build/doctrees docs/source docs/build/html

cdoc:
	rm -rf docs/build/*
	make doc


push-crowdin:
	ajenti-dev-multitool --xgettext
	ajenti-dev-multitool --push-crowdin

pull-crowdin:
	ajenti-dev-multitool --pull-crowdin
	ajenti-dev-multitool --msgfmt

check:
	ajenti-dev-multitool --find-outdated

upload:
	rm ajenti-core/dist/* ajenti-panel/dist/* || true
	cd ajenti-core && ./setup.py sdist && twine upload dist/*.tar.gz -i "Ajenti Packagers" -s
	cd ajenti-panel && ./setup.py sdist && twine upload dist/*.tar.gz -i "Ajenti Packagers" -s

upload-plugins: build
	rm plugins/dist/* || true
	ajenti-dev-multitool --setuppy 'sdist'
	twine upload plugins/*/dist/*.tar.gz -i "Ajenti Packagers" -s --skip-existing

test:
	cd e2e && ./run

build_dev:
	bash scripts/build_deb.sh

webdriver:
	cd e2e && node_modules/protractor/bin/webdriver-manager start

webdriver-update:
	cd e2e && node_modules/protractor/bin/webdriver-manager update

karma:
	cd tests-karma && node_modules/karma/bin/karma start karma.conf.coffee --no-single-run --auto-watch

nose:
	cd tests-nose && nosetests tests/
