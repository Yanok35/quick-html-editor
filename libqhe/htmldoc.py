import os
import re
#from gi.repository import GLib, Gtk, GtkSource
from gi.repository import GtkSource

class htmldoc(GtkSource.Buffer):
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

	def _regexp_made_absolute_path(self, matchobj):
		if len(matchobj.group(1)) == 0 or matchobj.group(1).find('://') != -1:
			return matchobj.group(0)
		elif len(matchobj.group(1)) and matchobj.group(1)[0] == '#':
			return matchobj.group(0)
		else:
			absolutepath = os.path.join(os.getcwd(), matchobj.group(1))
		return matchobj.group(0).replace(matchobj.group(1), absolutepath)

	def on_textbuf_changed(self, data):
		content = self.get_content_parsed()
		#print(content.decode('utf-8'))
		self.mainwindow.webview_upgrade(content)

	def get_content_parsed(self):
		content = self.get_property('text')

		# If localfile referenced in 'href' and 'src' attribute, add prefix:
		filepath_to_check = self.repattern.search(content)
		if filepath_to_check:
			content = self.repattern.sub(self._regexp_made_absolute_path, content)

		#print(content)
		return content

	def get_content(self):
		return self.get_property('text')


