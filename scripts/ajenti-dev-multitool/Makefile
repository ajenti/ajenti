upload:
	rm dist/*.tar.gz || true
	./setup.py sdist 
	twine upload --sign --identity "Ajenti Packagers" dist/*.tar.gz
