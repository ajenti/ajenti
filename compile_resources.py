#!/usr/bin/env python
import subprocess
import shutil
import glob
import os
import re

def compile_coffeescript(path):
	subprocess.check_output('coffee -o compiler-output -c "%s"' % path, shell=True)
	shutil.move(glob.glob('./compiler-output/*.js')[0], '%s.js' % path)
	shutil.rmtree('compiler-output')

def compile_less(path):
	pass

compilers = {
	r'.+\.coffee$': compile_coffeescript,
	r'.+\.less$': compile_less,
}


def compress_js(path):
	outpath = os.path.splitext(path)[0] + '.c.js'
	subprocess.check_output('yui-compressor --nomunge --disable-optimizations -o "%s" "%s"' % (outpath, path), shell=True)

def compress_css(path):
	outpath = os.path.splitext(path)[0] + '.c.css'
	subprocess.check_output('yui-compressor -o "%s" "%s"' % (outpath, path), shell=True)

compressors = {
	r'.+[^\.][^mc]\.js$': compress_js,
	r'.+[^\.][^mc]\.css$': compress_css,
}


def traverse(fx):
	plugins_path = './ajenti/plugins'
	for plugin in os.listdir(plugins_path):
		path = os.path.join(plugins_path, plugin, 'content')
		if os.path.exists(path):
			for name in os.listdir(path):
				file_path = os.path.join(path, name)
				fx(file_path)
				
def compile(file_path):
	for pattern in compilers:
		if re.match(pattern, file_path):
			compilers[pattern](file_path)

def compress(file_path):
	for pattern in compressors:
		if re.match(pattern, file_path):
			compressors[pattern](file_path)



traverse(compile)
traverse(compress)
