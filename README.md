quick-html-editor
=================

Overview
--------

This tool aim to be a WYSIWYG Html editor to render PDF. It's a simple binding
between an GtkSourceView editor, a web renderer and an Evince previewer.
PDF generation is linked to an external tool named [Weasyprint](http://weasyprint.org/)
but other tools such as [Prince](http://www.princexml.com/) can be used as well.

Quick setup guide
-----------------

Follow these steps to install the Quick HTML Editor on your machine.

1. First, prepare a Virtual Environment for python:

	```
	virtualenv --system-site-packages quick-html-venv
	cd quick-html-venv/
	source ./bin/activate
	```

2. Install dependencies:

	```
	pip install WeasyPrint
	```

3. Clone this git repository:

	```
	git clone https://github.com/Yanok35/quick-html-editor.git
	```

Running
-------

Simply launch :

```
cd quick-html-venv/
source ./bin/activate
cd quick-html-editor/
./quick-html.py
```

Dependency list
---------------

* Gtk (3.10.8)
* WeasyPrint (0.23)
* Gobject Introspection for Evince : gir1.2-evince-3.0 (deb package)

On debian based system, you can install following system packages:
	```
	apt-get install python-gi python-gi-cairo python-gtksourceview2
	```
