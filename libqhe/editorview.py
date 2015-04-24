
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from gi.repository import Gtk, GtkSource, Pango

class editorview(Gtk.VPaned):

    def __init__(self, textbuf=None):
        super(editorview, self).__init__()

        cssScroll, self.cssview = self._scroll_sourceview_new(textbuf)
        htmlScroll, self.htmlview = self._scroll_sourceview_new(textbuf)

        self.pack1(cssScroll)
        self.pack2(htmlScroll)
        self.set_position(450/2)

    def _scroll_sourceview_new(self, textbuf):

        if textbuf:
            sourceview = GtkSource.View(buffer=textbuf)
        else:
            sourceview = GtkSource.View()
        sourceview.set_show_line_numbers(True)
        sourceview.set_highlight_current_line(True)
        #sourceview.set_wrap_mode(True)
        fontdesc = Pango.FontDescription("Monospace 11")
        sourceview.modify_font(fontdesc)
        scroll = Gtk.ScrolledWindow()
        scroll.add(sourceview)

        return scroll, sourceview

    def set_buffer(self, textbuf):
        self.cssview.set_buffer(textbuf)
        self.htmlview.set_buffer(textbuf)
