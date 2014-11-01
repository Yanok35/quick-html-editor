#from gi.repository import GLib, Gtk, GtkSource
from gi.repository import GtkSource

class htmldoc(GtkSource.Buffer):
	def __init__(self):
		super(htmldoc, self).__init__()

		lm = GtkSource.LanguageManager.new()
	        language = lm.get_language('html')
		self.set_language(language)
	        self.set_highlight_syntax(True)
	
	def get_name(self):
		return "hello"


