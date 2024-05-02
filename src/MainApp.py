import os

import gi
import cairo

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk

import src.AppWindow
from src.DvdManager import DvdManager

class MainApp(Gtk.Application):
    def __init__(self, main_script_dir):
        super().__init__(application_id='de.sakurajin.dvdextractor')

        self.main_script_dir = main_script_dir
        self.main_window = None
        self.dvd_manager = None

    def do_activate(self):
        builder = Gtk.Builder()
        ui_file = os.path.join(self.main_script_dir, 'src', 'ui', 'dvdextractor.ui')
        builder.add_from_file(ui_file)

        # Obtain the button widget and connect it to a function
        # button = builder.get_object("button1")
        # button.connect("clicked", self.hello)

        # Obtain and show the main window
        self.main_window = builder.get_object("MainAppWindow")

        # Setup the menu
        self.__create_menu_actions()
        self.set_menubar(builder.get_object("MainMenu"))

        self.main_window.set_application(self)
        self.main_window.present()

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def __create_menu_actions(self):
        action = Gio.SimpleAction.new("selectFile")
        action.connect("activate", self._select_file)
        Gio.ActionMap.add_action(self, action)

        action = Gio.SimpleAction.new("quit")
        action.connect("activate", self._on_close)
        Gio.ActionMap.add_action(self, action)

    def _on_close(self, *_):
        self.main_window.close()

    def _select_file(self, *_):
        dialog = Gtk.FileDialog(title="Select DVD")

        _iso_filter = Gtk.FileFilter()
        _iso_filter.set_name("DVD image files")
        _iso_filter.add_pattern("*.iso")
        dialog.set_default_filter(_iso_filter)

        dialog.open(parent=self.main_window, callback=self._dvd_file_selected)

    def _dvd_file_selected(self, source_dialog, res):
        try:
            file = source_dialog.open_finish(res).get_path()
            print(f"Selected file: {file}")

            self.dvd_manager = DvdManager(file)
            self.dvd_manager.print_title_info()

        except Exception as e:
            pass
