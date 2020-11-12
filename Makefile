## Flag for custom config file
CONFIGFILE := ''

all: build

bower:
	ajenti-dev-multitool --bower install

build:
	ajenti-dev-multitool --msgfmt
	ajenti-dev-multitool --build

run:
	cd ajenti-panel && ./ajenti-panel -v --autologin --plugins ../plugins $(CONFIGFILE)

rundev:
	cd ajenti-panel && ./ajenti-panel -v --autologin --plugins ../plugins --dev $(CONFIGFILE)

rundevlogin:
	cd ajenti-panel && ./ajenti-panel -v --plugins ../plugins --dev $(CONFIGFILE)

runprod:
	cd ajenti-panel && ./ajenti-panel --plugins ../plugins $(CONFIGFILE)

rund:
	cd ajenti-panel && ./ajenti-panel --plugins ../plugins -d $(CONFIGFILE)


clean:
	find | grep \.pyc | xargs rm || true
	rm -rf plugins/*/build || true
	rm -rf plugins/*/dist || true
	rm -rf plugins/*/.last-upload || true


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
	cd ajenti-core && ./setup.py sdist && twine upload dist/*.tar.gz -i "Ajenti Packagers" -s
	cd ajenti-panel && ./setup.py sdist && twine upload dist/*.tar.gz -i "Ajenti Packagers" -s

upload-plugins: build
	ajenti-dev-multitool --setuppy 'sdist upload --sign --identity "Ajenti Packagers"'

test:
	cd e2e && ./run


webdriver:
	cd e2e && node_modules/protractor/bin/webdriver-manager start

webdriver-update:
	cd e2e && node_modules/protractor/bin/webdriver-manager update

karma:
	cd tests-karma && node_modules/karma/bin/karma start karma.conf.coffee --no-single-run --auto-watch

nose:
	cd tests-nose && nosetests tests/
