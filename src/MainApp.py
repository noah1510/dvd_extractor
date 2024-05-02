import multiprocessing
import os

import gi
import cairo

from src import VideoExtractor
from src.DvdManager import DvdManager

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk


from src.ConfigManager import ConfigManager


class MainApp(Gtk.Application):
    def __init__(self, main_script_dir):
        super().__init__(application_id='de.sakurajin.dvdextractor')

        self.main_script_dir = main_script_dir

        self.main_window = None
        self.title_list_box = None
        self.config_manager = None
        self.StartExtractionBtn = None

        self.dvd_manager = None
        self.selected_titles = None

    def do_activate(self):
        builder = Gtk.Builder()
        ui_file = os.path.join(self.main_script_dir, 'src', 'ui', 'dvdextractor.ui')
        builder.add_from_file(ui_file)

        # Obtain the button widget and connect it to a function
        self.StartExtractionBtn = builder.get_object("StartExtractionBtn")
        self.StartExtractionBtn.connect("clicked", self.__start_extraction)

        # Obtain and show the main window
        self.main_window = builder.get_object("MainAppWindow")
        self.title_list_box = builder.get_object("TitleListBox")
        self.config_manager = ConfigManager(builder.get_object("ConfigsListBox"), self.main_window)

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

            self.title_list_box.remove_all()
            self.selected_titles = {}

            titles = self.dvd_manager.get_title_list()
            for title in titles:
                title_button = Gtk.ToggleButton(label=f"Title {title.TitleNum}")
                title_button.connect("toggled", self.__toggle_title, title.TitleNum)
                title_button.set_active(True)
                self.title_list_box.append(title_button)

        except Exception as e:
            pass

    def __toggle_title(self, btn, title_num):
        title_str = str(title_num)
        if btn.get_active():
            self.selected_titles[title_str] = self.dvd_manager.create_title_dict(title_num)
        else:
            self.selected_titles.pop(title_str)

    def __start_extraction(self, btn):
        if not self.selected_titles:
            print("No titles selected for extraction")
            return

        print("Starting extraction")

        output_dir = self.config_manager.output_dir
        if not output_dir:
            output_dir = os.path.dirname(self.dvd_manager.path)

        handbrake_params = {}
        for title in self.selected_titles.values():
            handbrake_params[title['title_num']] = self.config_manager.get_handbrake_options(title)

        ffmpeg_params = self.config_manager.get_ffmpeg_concat_options(self.selected_titles)

        multiprocessing.Process(
            target=VideoExtractor.execute_extraction,
            args=(handbrake_params, ffmpeg_params, self.config_manager.keep_individual_titles, output_dir)
        ).start()

