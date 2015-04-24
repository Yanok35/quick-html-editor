#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import os
import signal
from optparse import OptionParser
from gi.repository import GLib, Gtk, GtkSource, Gdk, Pango

from libqhe.editorview import *
from libqhe.htmldoc import *
from libqhe.docbookdoc import *
from libqhe.pdfview import *

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
        self.set_size_request(800, 800)

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

        self.textbuf = htmldoc(self)
        self.editorview = editorview(self.textbuf)

        self.pdfview = pdfview()

        paned = Gtk.Paned()
        paned.pack1(self.editorview)
        paned.pack2(self.pdfview)
        paned.set_position(500)

        box.pack_start(paned, True, True, 0)

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

    def on_menu_file_print(self, widget):
        destfilename = os.path.join(os.getcwd(), 'export.pdf')
        content = self.textbuf.get_content_parsed()
        f = open(destfilename, 'w')
        f.write(content)
        f.close()
        print ('%s file saved.' % destfilename)

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

    def docpreview_update(self, htmlstr):
        self.pdfview.set_pdfcontent(htmlstr)

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

