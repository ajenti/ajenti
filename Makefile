## Flag for custom config file
CONFIGFILE := ''

all: build

build:
	python3 ./scripts/ajenti-dev-multitool/ajenti_dev_multitool.py --msgfmt
	python3 ./scripts/ajenti-dev-multitool/ajenti_dev_multitool.py --build-plugins

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

deb:
	python3 ./scripts/ajenti-dev-multitool/build_deb.py

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
	python3 ./scripts/ajenti-dev-multitool/ajenti_dev_multitool.py --xgettext
	python3 ./scripts/ajenti-dev-multitool/ajenti_dev_multitool.py --push-crowdin

pull-crowdin:
	python3 ./scripts/ajenti-dev-multitool/ajenti_dev_multitool.py --pull-crowdin
	python3 ./scripts/ajenti-dev-multitool/ajenti_dev_multitool.py --msgfmt

add-crowdin:
	python3 ./scripts/ajenti-dev-multitool/ajenti_dev_multitool.py --xgettext
	python3 ./scripts/ajenti-dev-multitool/ajenti_dev_multitool.py --add-crowdin

check:
	python3 ./scripts/ajenti-dev-multitool/ajenti_dev_multitool.py --find-outdated

upload:
	rm ajenti-core/dist/* ajenti-panel/dist/* || true
	cd ajenti-core && ./setup.py sdist && twine upload dist/*.tar.gz -i "Ajenti Packagers" -s
	cd ajenti-panel && ./setup.py sdist && twine upload dist/*.tar.gz -i "Ajenti Packagers" -s

upload-plugins: build
	rm plugins-new/*/dist/* || true
	python3 ./scripts/ajenti-dev-multitool/ajenti_dev_multitool.py --setuppy 'sdist'
	twine upload plugins-new/*/dist/*.tar.gz -i "Ajenti Packagers" -s --skip-existing

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
