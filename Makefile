all: build
	
bower:
	cd plugins && ajenti-dev-multitool --bower install

build:
	cd plugins && ajenti-dev-multitool --build

run:
	cd ajenti-panel && ./ajenti-panel -v --plugins ../plugins

rundev:
	cd ajenti-panel && ./ajenti-panel -v --dev --plugins ../plugins	

test:
	cd e2e && ./run