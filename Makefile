all: build

bower:
	cd plugins && ajenti-dev-multitool --bower install

build:
	cd plugins && ajenti-dev-multitool --build

run:
	cd ajenti-panel && ./ajenti-panel -v --autologin --plugins ../plugins

rundev:
	cd ajenti-panel && ./ajenti-panel -v --autologin --plugins ../plugins --dev

clean:
	find | grep \.pyc | xargs rm

check:
	cd plugins && ajenti-dev-multitool --find-outdated

upload: build
	cd ajenti-core && ./setup.py sdist upload
	cd ajenti-panel && ./setup.py sdist upload

upload-plugins: build
	cd plugins && ajenti-dev-multitool --setuppy 'sdist upload'

test:
	cd e2e && ./run

webdriver:
	cd e2e && node_modules/protractor/bin/webdriver-manager start

webdriver-update:
	cd e2e && node_modules/protractor/bin/webdriver-manager update

karma:
	cd tests-karma && node_modules/karma/bin/karma start karma.conf.coffee --no-single-run --auto-watch

