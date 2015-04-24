
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import docutils
import lxml.html
import os
import re
from lxml import etree
#from gi.repository import GLib, Gtk, GtkSource
from gi.repository import GtkSource
from .htmldoc import *

TEXT_DEFAULT="""================================
 reStructuredText Demonstration
================================

.. Above is the document title, and below is the subtitle.
   They are transformed from section titles after parsing.

--------------------------------
 Examples of Syntax Constructs
--------------------------------

.. bibliographic fields (which also require a transform):

:Author: David Goodger
:Address: 123 Example Street
          Example, EX  Canada
          A1B 2C3
"""

class rstdoc(htmldoc):
    def __init__(self, mainwindow):
        super(rstdoc, self).__init__(mainwindow)

        self.cssbuf = GtkSource.Buffer()
        self.cssbuf.connect('changed', self.on_cssbuf_changed)

        lm = GtkSource.LanguageManager.new()
        #language = lm.get_language('rest')
        #self.set_language(language)
        #self.set_highlight_syntax(True)

        language = lm.get_language('css')
        self.cssbuf.set_language(language)
        self.cssbuf.set_highlight_syntax(True)

        #self.xhtmlparser = etree.XMLParser(recover=True)
        
    def on_cssbuf_changed(self, data):
        print('oncss')
        content = self.get_property('text')
        self.emit('changed') # propagate 'changed' to main buffer

    def get_css_buffer(self):
        return self.cssbuf

    def get_content_parsed(self, content=None):
        if not content:
            content = self.get_property('text')

        try:
            # Convert RST to HTML in live
            template_rules = os.path.join(os.getcwd(), 'rst2html-template.txt')

            proc = subprocess.Popen(['/usr/bin/rst2html',
                     '--traceback', '--template=%s' % template_rules],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE)

            content, stderrdata = proc.communicate(content)
            
            # Use lxml to generate prepare stylesheet insertion
            if len(self.cssbuf.get_property('text')) > 0:
                html = lxml.html.fromstring(content)
                head_elem = html.find('head')
                css_node = etree.SubElement(head_elem, 'style')

                css_node.text = self.cssbuf.get_property('text')
                css_node.attrib["type"] = 'text/css'

                content = lxml.html.tostring(html, pretty_print=True)

                ### rootnode = etree.XML(content, self.xhtmlparser)
                ### rootnode.find

            #root = etree.XML(content, parser, base_url='file://' + os.getcwd())
            #root = etree.XML(content, parser)

            #print("content = ", content)
            # At this point, content is HTML
            #print(content)
            # Convert HTML to PDF
            content = super(rstdoc, self).get_content_parsed(content=content)
        except:
            print("exception")

        return content

    def new_file(self, filename):
        self.begin_not_undoable_action()
        self.set_text(TEXT_DEFAULT)
        self.end_not_undoable_action()

        self.filename = filename

