#!/usr/bin/env python

import os
import signal
from optparse import OptionParser
from gi.repository import GLib, Gtk, GtkSource, Gdk, Pango, WebKit
from libqhe.editorview import *
from libqhe.htmldoc import *
from libqhe.docbookdoc import *

UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action='DocumentMenu'>
      <menuitem action='DocumentNew' />
      <menuitem action='DocumentOpen' />
      <menuitem action='DocumentSave' />
      <menuitem action='DocumentClose' />
      <menuitem action='FilePrint' />
      <separator />
      <menuitem action='FileQuit' />
    </menu>
    <!--menu action='EditMenu'>
      <menuitem action='EditCopy' />
      <menuitem action='EditPaste' />
      <menuitem action='EditSomething' />
    </menu-->
    <menu action='ChoicesMenu'>
      <menuitem action='ChoiceOne'/>
      <menuitem action='ChoiceTwo'/>
      <separator />
      <menuitem action='ChoiceThree'/>
    </menu>
  </menubar>
  <toolbar name='ToolBar'>
    <toolitem action='DocumentNew' />
    <toolitem action='DocumentOpen' />
    <toolitem action='DocumentSave' />
    <toolitem action='DocumentClose' />
    <separator />
    <toolitem action='FilePrintPreview' />
    <toolitem action='FilePrint' />
    <toolitem action='FileQuit' />
  </toolbar>
  <popup name='PopupMenu'>
    <menuitem action='EditCopy' />
    <menuitem action='EditPaste' />
    <menuitem action='EditSomething' />
  </popup>
</ui>
"""

APP_VERSION_MAJOR=0
APP_VERSION_MINOR=1
MAINWIN_TITLE_DEFAULT="Quick Html Editor"

class MenuExampleWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title=MAINWIN_TITLE_DEFAULT)

        self.set_default_size(200, 200)

        action_group = Gtk.ActionGroup("my_actions")

        self.add_file_menu_actions(action_group)
        self.add_edit_menu_actions(action_group)
        self.add_choices_menu_actions(action_group)

        uimanager = self.create_ui_manager()
        uimanager.insert_action_group(action_group)

        menubar = uimanager.get_widget("/MenuBar")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menubar, False, False, 0)

        toolbar = uimanager.get_widget("/ToolBar")
        box.pack_start(toolbar, False, False, 0)

        #eventbox = Gtk.EventBox()
        #eventbox.connect("button-press-event", self.on_button_press_event)
        #box.pack_start(eventbox, True, True, 0)
        ###vbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        ###vbox.pack_start

        self.textbuf = htmldoc(self)
        self.editorview = editorview(self.textbuf)

        self.webView = WebKit.WebView()
        websettings = self.webView.get_settings()
        websettings.set_property('enable-file-access-from-file-uris', False)
        self.webView.set_settings(websettings)
        self.webView.connect('title-changed', self.on_webview_title_changed)

        #self.webView.load_string(self.textbuf.get_content_parsed(), 'text/html', 'utf-8', 'file://')
        #self.webView.load_string(TEXT_DEFAULT, 'text/html', 'utf-8', 'file:///home/yannick/python/tst3/')
        #self.webView.load_html_string(TEXT_DEFAULT, 'file:///home/yannick/python/tst3/')
        #self.webView.load_uri('file:///home/yannick/python/tst3/doc.html')
        #self.webView.load_uri('file:///home/yannick/python/a4_pages/index.html')
        #self.webView.set_editable(True)
        scrolled_preview = Gtk.ScrolledWindow()
        scrolled_preview.add(self.webView)
        self.vadjust = scrolled_preview.get_vadjustment()
        self.vadjust_latest = 0.0
        self.vadjust.connect('changed', self.on_vadjust_changed)

        paned = Gtk.Paned()
        paned.pack1(self.editorview)
        paned.pack2(scrolled_preview)
        paned.set_position(500)

        box.pack_start(paned, True, True, 0)

        #label = Gtk.Label("Right-click to see the popup menu.")
        #eventbox.add(label)

        self.popup = uimanager.get_widget("/PopupMenu")

        self.add(box)

        self.connect('destroy', self.on_destroy)

    def on_destroy(self, data):
        self.textbuf.__del__()

    def add_file_menu_actions(self, action_group):
        action_documentmenu = Gtk.Action("DocumentMenu", "Document", None, None)
        action_group.add_action(action_documentmenu)

        action_new = Gtk.Action("DocumentNew", "_New",
            "Create a new document", Gtk.STOCK_NEW)
        action_new.connect("activate", self.on_menu_document_new)
        action_group.add_action_with_accel(action_new, None)

        action_new = Gtk.Action("DocumentOpen", "_Open",
            "Open an existing document", Gtk.STOCK_OPEN)
        action_new.connect("activate", self.on_menu_document_open)
        action_group.add_action_with_accel(action_new, None)

        action_new = Gtk.Action("DocumentSave", "_Save",
            "Save the current document", Gtk.STOCK_SAVE)
        action_new.connect("activate", self.on_menu_document_save)
        action_group.add_action_with_accel(action_new, None)

        action_new = Gtk.Action("DocumentClose", "_Close",
            "Close the current document", Gtk.STOCK_CLOSE)
        action_new.connect("activate", self.on_menu_document_close)
        action_group.add_action_with_accel(action_new, None)

        action_fileprintpreview = Gtk.Action("FilePrintPreview", None, None, Gtk.STOCK_PRINT_PREVIEW)
        action_fileprintpreview.connect("activate", self.on_menu_file_print_preview)
        action_group.add_action_with_accel(action_fileprintpreview, None)

        action_fileprint = Gtk.Action("FilePrint", None, None, Gtk.STOCK_PRINT)
        action_fileprint.connect("activate", self.on_menu_file_print)
        action_group.add_action_with_accel(action_fileprint, None)

        action_filequit = Gtk.Action("FileQuit", None, None, Gtk.STOCK_QUIT)
        action_filequit.connect("activate", self.on_menu_file_quit)
        action_group.add_action(action_filequit)


    def add_edit_menu_actions(self, action_group):
        pass
        #action_group.add_actions([
        #    ("EditMenu", None, "Edit"),
        #    ("EditCopy", Gtk.STOCK_COPY, None, None, None,
        #     self.on_menu_others),
        #    ("EditPaste", Gtk.STOCK_PASTE, None, None, None,
        #     self.on_menu_others),
        #    ("EditSomething", None, "Something", "<control><alt>S", None,
        #     self.on_menu_others)
        #])

    def add_choices_menu_actions(self, action_group):
        action_group.add_action(Gtk.Action("ChoicesMenu", "Choices", None,
            None))

        action_group.add_radio_actions([
            ("ChoiceOne", None, "One", None, None, 1),
            ("ChoiceTwo", None, "Two", None, None, 2)
        ], 1, self.on_menu_choices_changed)

        three = Gtk.ToggleAction("ChoiceThree", "Three", None, None)
        three.connect("toggled", self.on_menu_choices_toggled)
        action_group.add_action(three)

    def create_ui_manager(self):
        uimanager = Gtk.UIManager()

        # Throws exception if something went wrong
        uimanager.add_ui_from_string(UI_INFO)

        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        self.add_accel_group(accelgroup)
        return uimanager

    def set_current_doc(self, filename):
        if filename and os.path.exists(filename):
            (f, ext) = os.path.splitext(filename)
            if ext == '.docbook' or ext == '.xml':
                self.textbuf = docbookdoc(self)
            else:
                self.textbuf = htmldoc(self)
            self.editorview.set_buffer(self.textbuf)
            self.textbuf.open_file(filename)
        else:
            self.textbuf.new_file(filename)

    def on_menu_document_new(self, widget):
        self.textbuf.new_file(None)

    def on_menu_document_open(self, widget):
        print("A File|Open menu item was selected.")

    def on_menu_document_save(self, widget):
        self.textbuf.save_file()

    def on_menu_document_close(self, widget):
        print("A File|Close menu item was selected.")

    def on_menu_file_print_preview(self, widget):
        # 
        destfilename = os.path.join(os.getcwd(), 'export.pdf')
        print ("Preview %s" % destfilename)
        mainframe = self.webView.get_main_frame()
        printop = Gtk.PrintOperation()
        printop.set_property('export-filename', destfilename)
        #mainframe.print_full(printop, Gtk.PrintOperationAction.EXPORT)
        #os.system("evince %s" % destfilename)
        mainframe.print_full(printop, Gtk.PrintOperationAction.PREVIEW)

    def on_menu_file_print(self, widget):
        #
        destfilename = os.path.join(os.getcwd(), 'export.pdf')
        if 0 == 1:
            print ("Printing %s" % destfilename)
            mainframe = self.webView.get_main_frame()
            printop = Gtk.PrintOperation()
            printop.set_property('export-filename', destfilename)
            mainframe.print_full(printop, Gtk.PrintOperationAction.EXPORT)
            os.system("evince %s" % destfilename)
        else:
            import subprocess

           ############################################################################ self.webView.get_html()
            proc = subprocess.Popen(['weasyprint',
                                     '--base-url', '"file://"', '-', destfilename],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            )

            content = self.textbuf.get_content_parsed()
            proc.stdin.write(content)
            proc.stdin.close()
            proc.wait()

        #os.system("evince %s" % destfilename)
        

    def on_menu_file_quit(self, widget):
        Gtk.main_quit()

    def on_menu_others(self, widget):
        print("Menu item " + widget.get_name() + " was selected")

    def on_menu_choices_changed(self, widget, current):
        print(current.get_name() + " was selected.")

    def on_menu_choices_toggled(self, widget):
        if widget.get_active():
            print(widget.get_name() + " activated")
        else:
            print(widget.get_name() + " deactivated")

    def on_button_press_event(self, widget, event):
        # Check if right mouse button was preseed
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.popup.popup(None, None, None, None, event.button, event.time)
            return True # event has been handled

    def on_webview_title_changed(self, webView, frame, title):
        filename = self.textbuf.get_filename()
        if not filename:
            filename = '*scratch*'
        wintitle = '[%s]' % filename
        wintitle = "%s %s" % (MAINWIN_TITLE_DEFAULT, wintitle)
    	if len(title):
            wintitle = "%s - %s" % (title, wintitle)

        self.set_title(wintitle)

    def webview_upgrade(self, htmlstr):
        self.webView.load_string(htmlstr,  'text/html', 'utf-8', 'file://')

    def on_vadjust_changed(self, data):
        # After redrawed, webkit widget go down to 0, and vadjust is returning to top.
        if self.vadjust.get_value() == 0.0:
            self.vadjust.set_value(self.vadjust_latest)
        else:
            self.vadjust_latest = self.vadjust.get_value()
        #print('on_vadjust_changed', self.vadjust.get_lower(), self.vadjust.get_value(), self.vadjust.get_upper())

    #def get_preview_slidepos(self):
    #    high = self.vadjust.get_upper()
    #    low  = self.vadjust.get_lower()
    #    delta = float(high - low)
    #    if delta != 0.0:
    #        return self.vadjust.get_value() / delta
    #    else:
    #        return 0.0

def main():
	parser = OptionParser(version=MAINWIN_TITLE_DEFAULT + " - v%d.%d" % (APP_VERSION_MAJOR, APP_VERSION_MINOR))
	(options, args) = parser.parse_args()

	if (len(args) > 0):
		filename = args[0]
	else:
		filename = None

	print (options, args)
	#os._exit(0)

	signal.signal(signal.SIGINT, signal_handler)

        # Use threads
        GLib.threads_init()
        Gdk.threads_init()

	window = MenuExampleWindow()
	window.set_current_doc(filename)
	window.resize(1400, 500)
	window.connect("delete-event", Gtk.main_quit)
	window.show_all()

        #thread = threading.Thread(target=app.thr_main)
        #thread.start()

	Gdk.threads_init()
	Gtk.main()
	Gdk.threads_leave()

        #thread.join()

def signal_handler(signal, frame):
	#print('You pressed Ctrl+C!')
	Gtk.main_quit()
	#sys.exit(0)

if __name__ == "__main__":
        main()

