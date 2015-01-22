all: build

bower:
	cd plugins && ajenti-dev-multitool --bower install

build:
	cd plugins && ajenti-dev-multitool --build

run:
	cd ajenti-panel && ./ajenti-panel -v --autologin --plugins ../plugins

rundev:
	cd ajenti-panel && ./ajenti-panel -v --autologin --plugins ../plugins --dev

test:
	cd e2e && ./run