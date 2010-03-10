def info(c,s):
	d = '(Unknown)\t'
	if (c != None and c != ''):
		d = '(' + c + ')\t'
	d = brown(d)
	print green('[INFO]\t'), d, s
	
def err(c,s):
	d = '(Unknown)\t'
	if (c != None and c != ''):
		d = '(' + c + ')\t'
	d = brown(d)
	print red('[ERR]\t'), d, s
	
def warn(c,s):
	d = '(Unknown)\t'
	if (c != None and c != ''):
		d = '(' + c + ')\t'
	d = brown(d)
	print yellow('[WARN]\t'), d, s
	
	
	
	
	
	
	
	
# Copyright 1998-2003 Daniel Robbins, Gentoo Technologies, Inc.
# Distributed under the GNU Public License v2
# $Header: /home/cvsroot/gentoo-src/portage/pym/output.py,v 1.16 2003/05/29 08:34:55 carpaski Exp $

import os,sys

havecolor=1
dotitles=1

codes={}
codes["reset"]="\x1b[0m"
codes["bold"]="\x1b[01m"

codes["teal"]="\x1b[36;06m"
codes["turquoise"]="\x1b[36;01m"

codes["fuscia"]="\x1b[35;01m"
codes["purple"]="\x1b[35;06m"

codes["blue"]="\x1b[34;01m"
codes["darkblue"]="\x1b[34;06m"

codes["green"]="\x1b[32;01m"
codes["darkgreen"]="\x1b[32;06m"

codes["yellow"]="\x1b[33;01m"
codes["brown"]="\x1b[33;06m"

codes["red"]="\x1b[31;01m"
codes["darkred"]="\x1b[31;06m"

def xtermTitle(mystr):
	if havecolor and dotitles and os.environ.has_key("TERM"):
		myt=os.environ["TERM"]
		if myt in ["xterm","Eterm","aterm","rxvt"]:
			sys.stderr.write("\x1b]1;\x07\x1b]2;"+str(mystr)+"\x07")
			sys.stderr.flush()

def xtermTitleReset():
	if havecolor and dotitles and os.environ.has_key("TERM"):
		myt=os.environ["TERM"]
		xtermTitle(os.environ["TERM"])


def notitles():
	"turn off title setting"
	dotitles=0

def nocolor():
	"turn off colorization"
	havecolor=0
	for x in codes.keys():
		codes[x]=""

def resetColor():
	return codes["reset"]

def ctext(color,text):
	return codes[ctext]+text+codes["reset"]

def bold(text):
	return codes["bold"]+text+codes["reset"]
def white(text):
	return bold(text)

def teal(text):
	return codes["teal"]+text+codes["reset"]
def turquoise(text):
	return codes["turquoise"]+text+codes["reset"]
def darkteal(text):
	return turquoise(text)

def fuscia(text):
	return codes["fuscia"]+text+codes["reset"]
def purple(text):
	return codes["purple"]+text+codes["reset"]

def blue(text):
	return codes["blue"]+text+codes["reset"]
def darkblue(text):
	return codes["darkblue"]+text+codes["reset"]

def green(text):
	return codes["green"]+text+codes["reset"]
def darkgreen(text):
	return codes["darkgreen"]+text+codes["reset"]

def yellow(text):
	return codes["yellow"]+text+codes["reset"]
def brown(text):
	return codes["brown"]+text+codes["reset"]
def darkyellow(text):
	return brown(text)

def red(text):
	return codes["red"]+text+codes["reset"]
def darkred(text):
	return codes["darkred"]+text+codes["reset"]

