__author__ = 'chance'

import sys

#from git import Repo
#import html

python_version = sys.version
python_version_root = python_version[0]
if ( python_version_root == '3'):
    print( "FATAL ERROR: Run this script using python2 (the html package is not compatible)")
    exit(1)

from html import HTML

def html_line(text,plus=0):
    h = HTML()
    p = ""
    if(plus):
        p = plus
    h.p(str(text)+p)
    f.write(str(h))

def html_hr():
    h = HTML()
    f.write(str(h.hr))

def html_img():
    h = HTML()
    f.write(str(h.img("src='the-forum.jpg'")))

html_head = "<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>Stub</title><link href='stub.css' rel='stylesheet' type='text/css'></head><body><hr>"
html_footer = "</body></html>"

h = HTML()

outfile_name = "test_html.html"

f = open(outfile_name, "w")

f.write(html_head)

html_line('Hello, world!')
html_line('Hello, world!!')
html_line('Hello, world!!!!')
f.write("<img src='the-forum.jpg'>")

f.write(html_footer)

print( "wrote to " + outfile_name )

f.close()

