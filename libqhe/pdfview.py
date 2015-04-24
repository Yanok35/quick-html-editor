
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import os

from gi.repository import GLib, Gtk, Gio
from gi.repository import EvinceDocument
from gi.repository import EvinceView

class pdfview(Gtk.ScrolledWindow):

    def __init__(self, filename=None):
        super(pdfview, self).__init__()

        EvinceDocument.init()
        view = EvinceView.View()
        self.view = view
        self.model = None
        self.current_pages = 0

        if filename:
            self.set_document()

        self.add(view)

    def set_document(self, filename):
        if os.path.isabs(filename):
            url = 'file://' + filename
        else:
            url = 'file://' + os.path.join(os.getcwd(), filename)

        if self.model:
            self.model.get_document().load(url)
            self.view.reload()
        else:
            model = EvinceView.DocumentModel()
            self.model = model
            doc = EvinceDocument.Document.factory_get_document(url)
            model.set_document(doc)

            self.view.set_model(model)

    def set_pdfcontent(self, pdfcontent):

        bytes = GLib.Bytes.new(pdfcontent)
        stream = Gio.MemoryInputStream.new_from_bytes(bytes)

        # The following optimization made the apps to crash sometimes...
        #if self.model:
        #    doc = self.model.get_document()
        #    nb_before = doc.get_n_pages()
        #    doc.load_stream(stream,
        #        EvinceDocument.DocumentLoadFlags.NONE,
        #        None)
        #    nb_after = doc.get_n_pages()
        #    if nb_after == nb_before:
        #        self.view.reload()
        #        return

        # We enter here the first time to create the Document Model
        #  and also when the total number of pages has changed
        current_page = 0
        if self.model:
            current_page = self.model.get_property('page')

        model = EvinceView.DocumentModel()
        doc = EvinceDocument.Document.factory_get_document_for_stream(
            stream,
            'application/pdf', 
            EvinceDocument.DocumentLoadFlags.NONE,
            None)
        model.set_document(doc)

        if current_page > doc.get_n_pages():
            current_page = doc.get_n_pages()
        model.set_page(current_page)

        self.view.set_model(model)
        self.model = model

