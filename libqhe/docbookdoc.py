import os
import re
#from gi.repository import GLib, Gtk, GtkSource
from gi.repository import GtkSource
from .htmldoc import *

TEXT_DEFAULT="""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE chapter PUBLIC "-//OASIS//DTD DocBook XML V4.5//EN"
"http://www.oasis-open.org/docbook/xml/4.5/docbookx.dtd">
<chapter>
  <title>Chapter Title Here</title>

  <para>If you have any opening text before the first section heading, put it
  here. (Do not use a <literal>&lt;sect1&gt;</literal> with an empty
  <literal>&lt;title&gt;</literal>.) If you want to start your chapter with a
  section heading, just delete this <literal>&lt;para&gt;</literal>.</para>

  <sect1>
    <title>Section Title Here</title>

    <para>Opening para...</para>
  </sect1>
</chapter>
"""

class docbookdoc(htmldoc):
	def __init__(self, mainwindow):
		super(docbookdoc, self).__init__(mainwindow)

	def get_content_parsed(self):
		content = self.get_property('text')

		import subprocess

		p = subprocess.Popen(["pandoc", "-f", "docbook", "-t", "html5"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		(stdoutdata, stderrdata) = p.communicate(content)

		return stdoutdata

	def new_file(self, filename):
		self.begin_not_undoable_action()
		self.set_text(TEXT_DEFAULT)
		self.end_not_undoable_action()

		self.filename = filename

