#!/usr/bin/env python

import os
import re
from gi.repository import GLib, Gtk, GtkSource, Gdk, Pango, WebKit

UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menu action='FileNew'>
        <menuitem action='FileNewStandard' />
        <menuitem action='FileNewFoo' />
        <menuitem action='FileNewGoo' />
      </menu>
      <menuitem action='FilePrint' />
      <separator />
      <menuitem action='FileQuit' />
    </menu>
    <menu action='EditMenu'>
      <menuitem action='EditCopy' />
      <menuitem action='EditPaste' />
      <menuitem action='EditSomething' />
    </menu>
    <menu action='ChoicesMenu'>
      <menuitem action='ChoiceOne'/>
      <menuitem action='ChoiceTwo'/>
      <separator />
      <menuitem action='ChoiceThree'/>
    </menu>
  </menubar>
  <toolbar name='ToolBar'>
    <toolitem action='FileNewStandard' />
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

__TEXT_DEFAULT="""<!DOCTYPE html>
<html>
 <head>
  <meta charset="utf-8" />
  <link rel="stylesheet" href="a4.css">
  <title>Document Title</title>
  <style TYPE="text/css">
    body {
     background: #e8eeee;
     color: #80c0c0 }
    h1, h2 { color: #800000; }
  </style>
 </head>
 <body>
  <page size="A4">
  <h2>Hello World !</h2>
  </page>
 </body>
</html>
"""

TEXT_DEFAULT="""<!DOCTYPE html>
<html>
 <head>
  <meta charset="utf-8" />
  <title>Document Title</title>
  <style TYPE="text/css">
    body {
      background: rgb(204,204,204); 
      text-align: justify;
    }
    page[size="A4"] {
      background: white;
      width: 21cm;
      height: 29.7cm;
      display: block;
      margin: 0 auto;
      margin-bottom: 16px;
      box-shadow: 0px 0px 8px 2px rgba(0,0,0,0.5);
    }
    h1 {
      //margin-left: 5cm;
      text-align: center;
    }
    @page { size: A4; margin: 0cm }
    @media print {
      body, page[size="A4"] {
        background: none;
        margin: 0 0 0 0;
        margin-top: 0cm;
        margin-left: 0cm;
        margin-right: 0cm;
        margin-bottom: 0cm;
        border: 0cm;
        box-shadow: 0 0 0 0;
      }
    }
  </style>
 </head>
 <body>
  <page size="A4">
  <title> This is the title </title>
  <h2>Hello World !</h2>
  <center><img src='samples/fig1.png' /></center>
  </page>
  <page size="A4">
  <h2>page 2</h2>
  </page>
 </body>
</html>
"""

_TEXT_DEFAULT="""<!DOCTYPE html>
<html>
 <head>
  <meta charset="utf-8" />
  <title>Document Title</title>
  <style TYPE="text/css">
    body {
      background: white; 
      text-align: justify;
    }
    h1 {
      //margin-left: 5cm;
      text-align: center;
    }
    @page { size: A4; margin: 0cm }
  </style>
 </head>
 <body>
  <page size="A4">
  <title> This is the title </title>
  <h2>Hello World !</h2>
  <center><img src='fig1.png' /></center>
  </page>
  <page size="A4">
  <h2>page 2</h2>
  </page>
 </body>
</html>
"""

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

        #textview = Gtk.TextView()
        textview = GtkSource.View.new()
        textview.set_show_line_numbers(True)
        textview.set_highlight_current_line(True)
        fontdesc = Pango.FontDescription("Monospace 11")
        textview.modify_font(fontdesc)
        scrolled_textview = Gtk.ScrolledWindow()
        scrolled_textview.add(textview)
        #self.textbuf = textview.get_property('buffer')

        lm = GtkSource.LanguageManager.new()
        #language = lm.get_language_ids() # list all language
        language = lm.get_language('html') # list all language
        self.textbuf = GtkSource.Buffer.new_with_language(language)
        #self.textbuf = GtkSource.Buffer.new()
        self.textbuf.set_highlight_syntax(True)
        textview.set_buffer(self.textbuf)
        self.textbuf.connect('changed', self.on_textbuf_changed)
        self.textbuf.set_text(TEXT_DEFAULT)

        self.webView = WebKit.WebView()
        websettings = self.webView.get_settings()
        websettings.set_property('enable-file-access-from-file-uris', False)
        self.webView.set_settings(websettings)
        self.webView.connect('title-changed', self.on_webview_title_changed)

        self.webView.load_string(TEXT_DEFAULT, 'text/html', 'utf-8', 'file://')
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
        paned.pack1(scrolled_textview)
        paned.pack2(scrolled_preview)
        paned.set_position(1400/2)

        self.scrolled_textview = scrolled_textview
        self.scrolled_preview = scrolled_preview
        box.pack_start(paned, True, True, 0)

        #label = Gtk.Label("Right-click to see the popup menu.")
        #eventbox.add(label)

        self.popup = uimanager.get_widget("/PopupMenu")

        self.add(box)

	# Regular expression to add prefix for local file
        self.repattern = re.compile("(?:href|src)[ \t\r\n]*=[ \t\r\n]*[\"'](.*)[\"']")

    def add_file_menu_actions(self, action_group):
        action_filemenu = Gtk.Action("FileMenu", "File", None, None)
        action_group.add_action(action_filemenu)

        action_filenewmenu = Gtk.Action("FileNew", None, None, Gtk.STOCK_NEW)
        action_group.add_action(action_filenewmenu)

        action_new = Gtk.Action("FileNewStandard", "_New",
            "Create a new file", Gtk.STOCK_NEW)
        action_new.connect("activate", self.on_menu_file_new_generic)
        action_group.add_action_with_accel(action_new, None)

        action_group.add_actions([
            ("FileNewFoo", None, "New Foo", None, "Create new foo",
             self.on_menu_file_new_generic),
            ("FileNewGoo", None, "_New Goo", None, "Create new goo",
             self.on_menu_file_new_generic),
        ])

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

    def on_menu_file_new_generic(self, widget):
        print("A File|New menu item was selected.")
        content = self.textbuf.get_property('text')
        self.webView.load_string(content,  'text/html', 'utf-8', 'file://')
        self.webView.reload()

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
            proc = subprocess.Popen(['/home/yannick/python/notebook/bin/weasyprint',
                                     '--base-url', '"file://"', '-', destfilename],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            )

            content = self.textbuf_get_content_parsed()
            proc.stdin.write(content)
            proc.stdin.close()
            proc.wait()

        os.system("evince %s" % destfilename)
        

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
    	if len(title):
            self.set_title ("%s - %s" % (MAINWIN_TITLE_DEFAULT, title))
        else:
            self.set_title (MAINWIN_TITLE_DEFAULT)

    def regexp_made_absolute_path(self, matchobj):
        if len(matchobj.group(1)) == 0 or matchobj.group(1).find('://') != -1:
            return matchobj.group(0)
        elif len(matchobj.group(1)) and matchobj.group(1)[0] == '#':
            return matchobj.group(0)
        else:
            absolutepath = os.path.join(os.getcwd(), matchobj.group(1))
            return matchobj.group(0).replace(matchobj.group(1), absolutepath)

    def textbuf_get_content_parsed(self):
        content = self.textbuf.get_property('text')

        # If localfile referenced in 'href' and 'src' attribute, add prefix:
        filepath_to_check = self.repattern.search(content)
        if filepath_to_check:
            content = self.repattern.sub(self.regexp_made_absolute_path, content)

        #print(content)
        return content

    def on_textbuf_changed(self, data):
        content = self.textbuf_get_content_parsed()
        #print(content.decode('utf-8'))

        #GLib.idle_add(self.webView.load_string, content, 'text/html', 'utf-8', '/')
        self.webView.load_string(content,  'text/html', 'utf-8', 'file://')

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
        # Use threads
        GLib.threads_init()

	window = MenuExampleWindow()     
	window.resize(1400, 500)
	window.connect("delete-event", Gtk.main_quit)
	window.show_all()

        #thread = threading.Thread(target=app.thr_main)
        #thread.start()

	Gtk.main()

        #thread.join()

if __name__ == "__main__":
        main()

