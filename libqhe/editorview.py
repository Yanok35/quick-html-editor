
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from gi.repository import Gtk, GtkSource, Pango

class editorview(Gtk.Notebook):

    def __init__(self, textbuf=None, cssbuf=None):
        super(editorview, self).__init__()

        if cssbuf is None:
            cssbuf = textbuf
        cssScroll, self.cssview = self._scroll_sourceview_new(cssbuf)
        htmlScroll, self.htmlview = self._scroll_sourceview_new(textbuf)

        #self.pack1(cssScroll)
        label = Gtk.Label.new('Content')
        self.append_page(htmlScroll, label)
        label = Gtk.Label.new('Rendering')
        self.append_page(cssScroll, label)
        #self.set_position(450/2)

    def _scroll_sourceview_new(self, textbuf):

        if textbuf:
            sourceview = GtkSource.View(buffer=textbuf)
        else:
            sourceview = GtkSource.View()
        sourceview.set_show_line_numbers(True)
        sourceview.set_highlight_current_line(True)
        sourceview.set_wrap_mode(Gtk.WrapMode.WORD)
        fontdesc = Pango.FontDescription("Monospace 11")
        sourceview.modify_font(fontdesc)
        scroll = Gtk.ScrolledWindow()
        scroll.add(sourceview)

        return scroll, sourceview

    def set_buffer(self, textbuf, cssbuf=None):
        if cssbuf is None:
            cssbuf = textbuf
        self.cssview.set_buffer(cssbuf)
        self.htmlview.set_buffer(textbuf)
