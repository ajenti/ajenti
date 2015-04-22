all: build

bower:
	cd plugins && ajenti-dev-multitool --bower install

build:
	cd plugins && ajenti-dev-multitool --build

run:
	cd ajenti-panel && ./ajenti-panel -v --autologin --plugins ../plugins

rundev:
	cd ajenti-panel && ./ajenti-panel -v --autologin --plugins ../plugins --dev

rundevlogin:
	cd ajenti-panel && ./ajenti-panel -v --plugins ../plugins --dev

runprod:
	cd ajenti-panel && ./ajenti-panel --plugins ../plugins


clean:
	find | grep \.pyc | xargs rm


doc:
	sphinx-build -b html -d docs/build/doctrees docs/source docs/build/html

cdoc:
	rm -rf docs/build/*
	make doc


check:
	cd plugins && ajenti-dev-multitool --find-outdated

upload: build
	cd ajenti-core && ./setup.py sdist upload --sign --identity "Ajenti Packagers"
	cd ajenti-panel && ./setup.py sdist upload --sign --identity "Ajenti Packagers"

upload-plugins: build
	cd plugins && ajenti-dev-multitool --setuppy 'sdist upload --sign --identity "Ajenti Packagers"'

test:
	cd e2e && ./run

webdriver:
	cd e2e && node_modules/protractor/bin/webdriver-manager start

webdriver-update:
	cd e2e && node_modules/protractor/bin/webdriver-manager update

karma:
	cd tests-karma && node_modules/karma/bin/karma start karma.conf.coffee --no-single-run --auto-watch

nose:
	cd tests-nose && nosetests base.py
