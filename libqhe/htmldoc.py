import os
import re
import subprocess
import threading
import time
from gi.repository import GtkSource, GObject

TEXT_DEFAULT="""<!DOCTYPE html>
<html>
 <head>
  <meta charset="utf-8" />
  <style TYPE="text/css">
    body {
      text-align: justify;
    }
    h1, h2 {
      text-align: center;
    }
    h3 {
      /*margin-left: 5cm;*/
      page-break-before: always;
      text-align: left;
    }
    @page {
        size: A4;
        margin: 2cm;
    }
    /* layout debug: */
    div, p {
        /*border-style: solid;*/
        border-width: .5pt;
    }
  </style>
 </head>
 <body>
 <div class="titlepage">
  <h1>Document title </h1>
  <h2>Subtitle </h2>
  <p>Below is an image integration example</p>
  <center><img src='samples/fig1.png' /></center>
 </div>

 <div>
  <h3>Section title</h3>
  <p>Here is a paragraph</p>
 </body>
</html>
"""

def idle_add_decorator(func):
	def callback(*args):
		GObject.idle_add(func, *args)
	return callback

class htmldoc(GtkSource.Buffer):
	"""
	This need to be class member, don't the reason in Threading
	implementation.
	"""
	thr_convert_stopevent = threading.Event()

	def __init__(self, mainwindow):
		super(htmldoc, self).__init__()

		# Regular expression to add prefix for local file
		self.repattern = re.compile("(?:href|src)[ \t\r\n]*=[ \t\r\n]*[\"'](.*)[\"']")

		lm = GtkSource.LanguageManager.new()
	        language = lm.get_language('html')
		self.set_language(language)
		self.set_highlight_syntax(True)

		self.connect('changed', self.on_textbuf_changed)

		self.mainwindow = mainwindow

	        self.filename = None

	        self.thr_convert_inputbuf = None
	        self.thr_convert_counter = 0
	        self.thr_convert = threading.Thread(target=self.thr_convert_main)
	        self.thr_convert.start()

	def __del__(self):
		self.thr_convert_stopevent.set()
		self.thr_convert.join()

	def _regexp_made_absolute_path(self, matchobj):
		if len(matchobj.group(1)) == 0 or matchobj.group(1).find('://') != -1:
			return matchobj.group(0)
		elif len(matchobj.group(1)) and matchobj.group(1)[0] == '#':
			return matchobj.group(0)
		else:
			absolutepath = os.path.join(os.getcwd(), matchobj.group(1))
		return matchobj.group(0).replace(matchobj.group(1), absolutepath)

	def on_textbuf_changed(self, data):
		content = self.get_property('text')
		self.thr_convert_inputbuf = content
		self.thr_convert_counter += 1

	def thr_convert_main(self):
		while not self.thr_convert_stopevent.is_set():
			if self.thr_convert_counter == 0:
				time.sleep(0.1) # 100ms
				continue
			self.thr_convert_counter = 0
			outbuf = self.get_content_parsed(self.thr_convert_inputbuf)
			if True: #if self.thr_convert_counter == 0:
				self.idle_docpreview_update(outbuf)

	@idle_add_decorator
	def idle_docpreview_update(self, content):
		self.mainwindow.docpreview_update(content)

	def get_content_parsed(self, content=None):
		if not content:
			content = self.get_property('text')

		# If localfile referenced in 'href' and 'src' attribute, add prefix:
		filepath_to_check = self.repattern.search(content)
		if filepath_to_check:
			content = self.repattern.sub(self._regexp_made_absolute_path, content)

		# Convert to PDF in live
		proc = subprocess.Popen(['weasyprint',
				     '-f', 'pdf', '-', '-'],
		#proc = subprocess.Popen(['prince',
		#		     '-', '-o', '-'],
			    stdin=subprocess.PIPE,
			    stdout=subprocess.PIPE,
			    )

		content, stderrdata = proc.communicate(content)

		#print(content)
		return content

	def get_content(self):
		return self.get_property('text')

	def set_filename(self, filename):
		self.filename = filename

	def get_filename(self):
		return self.filename

	def new_file(self, filename):
		self.begin_not_undoable_action()
		self.set_text(TEXT_DEFAULT)
		self.end_not_undoable_action()

		self.filename = filename

	def open_file(self, filename):
		if not (filename and os.path.exists(filename)):
			print ("file does not exists")
			return

		self.begin_not_undoable_action()
		f = open(filename, 'r')
		self.set_text(f.read())
		self.end_not_undoable_action()
		f.close()

		self.filename = filename

	def save_file(self):
		if not self.filename:
			print ("filename not set")
			return

		if not os.path.exists(self.filename) or self.can_undo():
			f = open(self.filename, 'w')
			f.write(self.get_property('text'))
			f.close()

			self.set_undo_manager(None)
		#else:
		#	print ("no change detected")

