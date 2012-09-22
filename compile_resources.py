#!/usr/bin/env python
import subprocess
import shutil
import glob
import os
import re
import sys


def compile_coffeescript(inpath):
	outpath = '%s.js' % inpath
	print ' - Coffee:\t%s -> %s' % (inpath, outpath)

	subprocess.check_output('coffee -o compiler-output -c "%s"' % inpath, shell=True)
	shutil.move(glob.glob('./compiler-output/*.js')[0], outpath)
	shutil.rmtree('compiler-output')

def compile_less(inpath):
	outpath = '%s.css' % inpath
	print ' - LESS:\t%s -> %s' % (inpath, outpath)
	print subprocess.check_output('lessc "%s" "%s"' % (inpath, outpath), shell=True)
	#print subprocess.check_output('recess --compile "%s" > "%s"' % (inpath, outpath), shell=True)

compilers = {
	r'.+\.coffee$': compile_coffeescript,
	r'.+[^i]\.less$': compile_less,
}


def compress_js(inpath):
	outpath = os.path.splitext(inpath)[0] + '.c.js'
	if not do_compress:
		return shutil.copy(inpath, outpath)
	print ' - YUI JS:\t%s -> %s' % (inpath, outpath)
	subprocess.check_output('yui-compressor --nomunge --disable-optimizations -o "%s" "%s"' % (outpath, inpath), shell=True)

def compress_css(inpath):
	outpath = os.path.splitext(inpath)[0] + '.c.css'
	if not do_compress:
		return shutil.copy(inpath, outpath)
	print ' - YUI CSS:\t%s -> %s' % (inpath, outpath)
	subprocess.check_output('yui-compressor -o "%s" "%s"' % (outpath, inpath), shell=True)

compressors = {
	r'.+[^\.][^mci]\.js$': compress_js,
	r'.+[^\.][^mci]\.css$': compress_css,
}


def traverse(fx):
	plugins_path = './ajenti/plugins'
	for plugin in os.listdir(plugins_path):
		path = os.path.join(plugins_path, plugin, 'content')
		if os.path.exists(path):
			for (dp,dn,fn) in os.walk(path):
				for name in fn:
					file_path = os.path.join(dp, name)
					fx(file_path)
				
def compile(file_path):
	for pattern in compilers:
		if re.match(pattern, file_path):
			compilers[pattern](file_path)

def compress(file_path):
	for pattern in compressors:
		if re.match(pattern, file_path):
			compressors[pattern](file_path)


do_compress = True
if len(sys.argv) > 1 and sys.argv[1] == 'nocompress':
	do_compress = False


traverse(compile)
traverse(compress)
