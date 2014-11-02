import os
import re
from lxml import etree
#from gi.repository import GLib, Gtk, GtkSource
from gi.repository import GtkSource
from .htmldoc import *

TEXT_DEFAULT="""<!DOCTYPE article PUBLIC "-//OASIS//DTD DocBook V3.1//EN">
<article>
<artheader>
<title>Docbook article introduction</title>
<author><honorific>M</honorific><firstname>Yannick</firstname>
<surname>Gicquel</surname></author>
</artheader>
<para> ... </para>
<section>
<title>Introduction</title>
<section>
<title>Welcome to the wonderful world of DocBook.</title>
<para>This tools is quite a good thing for <emphasis>real</emphasis> document
typesetting. It is possible to do cool stuff with this tool.
</section>
</para>
<para>Welcome to the wonderful world of DocBook.</para>
<para> ... </para>
</section>
<bibliography> ... </bibliography>
</article>
"""

class docbookdoc(htmldoc):
	def __init__(self, mainwindow):
		super(docbookdoc, self).__init__(mainwindow)

		xsl_url_html = "/usr/share/xml/docbook/stylesheet/docbook-xsl/html/docbook.xsl"
		if not os.path.exists(xsl_url_html):
			xsl_url_html = 'http://docbook.sourceforge.net/release/xsl/current/html/docbook.xsl'

		self.xsldocbooktranform = etree.XSLT(etree.parse(xsl_url_html))

	def get_content_parsed(self):
		content = self.get_property('text')

		parser = etree.XMLParser(recover=True)
		try:
			root = etree.XML(content, parser)

			consume_result = self.xsldocbooktranform(root)
			out = etree.tostring(consume_result, pretty_print=True)
			print (out)
			return out
		except:
			print("exception")

		return content

	def new_file(self, filename):
		self.begin_not_undoable_action()
		self.set_text(TEXT_DEFAULT)
		self.end_not_undoable_action()

		self.filename = filename

