import gi
import cairo

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk


class AppWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(400, 300)
        self.set_title("Hello World")

        self.connect("destroy", Gtk.main_quit)

        self.show_all()
