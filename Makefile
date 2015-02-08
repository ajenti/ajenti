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

test:
	cd e2e && ./run

webdriver:
	cd e2e && node_modules/protractor/bin/webdriver-manager start

webdriver-update:
	cd e2e && node_modules/protractor/bin/webdriver-manager update