import multiprocessing
import os

import gi
import cairo

from src.TaskManager import TaskManager
from src.TitleFinder import Title

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

        self.raw_title_list = None
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

            self.raw_title_list = Title.get_all_titles(file)

            self.title_list_box.remove_all()
            self.selected_titles = []

            for title in self.raw_title_list.values():
                title_button = Gtk.ToggleButton(label=f"Title {title.TitleNum} [{title.PlaybackTimeFancy}]")
                title_button.connect("toggled", self.__toggle_title, title.TitleNum)
                title_button.set_active(True)
                self.title_list_box.append(title_button)

        except Exception as e:
            print(e)

    def __toggle_title(self, btn, title_num):
        if btn.get_active():
            self.selected_titles.append(title_num)
        else:
            self.selected_titles.remove(title_num)

    def __start_extraction(self, btn):
        if not self.selected_titles:
            print("No titles selected for extraction")
            return

        print("Starting extraction")

        output_dir = self.config_manager.output_dir

        for title in self.selected_titles:
            print(f"Selected title: {title}")
            TaskManager.add_task(self.config_manager.get_handbrake_task(self.raw_title_list[title], output_dir))

        selected_titles_list = [self.raw_title_list[title] for title in self.selected_titles]
        concat_task = self.config_manager.get_concat_task(selected_titles_list, output_dir)
        if concat_task:
            TaskManager.add_task(concat_task)
