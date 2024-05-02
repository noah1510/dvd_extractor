import os
from typing import Dict, List

import jinja2
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk


class ConfigManager:
    def __init__(self, configs_list_box: Gtk.ListBox, main_window: Gtk.Window):
        self.configs_list_box = configs_list_box
        self.main_window = main_window

        self.keep_individual_titles = False
        self.concatenate_titles = True

        self.video_encoder = "svt_av1"
        self.quality = "22"
        self.encoder_preset = "8"

        self.audio_encoder = "opus"

        self.output_dir = None

        self.individual_title_name_template = (
            "{{base_stem}}-{{title_num}}.mkv"
        )
        self.concatenated_title_name_template = "{{base_stem}}.mkv"

        # Create the UI elements
        self.configs_list_box.append(Gtk.Separator())

        keep_individual_btn = Gtk.ToggleButton(label="Keep individual titles")
        keep_individual_btn.connect("toggled", self.__toggle_keep_individual)
        keep_individual_btn.set_active(self.keep_individual_titles)
        keep_individual_btn.set_margin_start(10)
        keep_individual_btn.set_margin_end(10)
        self.configs_list_box.append(keep_individual_btn)

        self.configs_list_box.append(Gtk.Separator())
        self.configs_list_box.append(Gtk.Label(label="Individual title name template:"))

        self.individual_title_name_text = Gtk.Text()
        self.individual_title_name_text.set_text(self.individual_title_name_template)
        self.configs_list_box.append(self.individual_title_name_text)

        self.configs_list_box.append(Gtk.Separator())

        concatenate_btn = Gtk.ToggleButton(label="Concatenate titles")
        concatenate_btn.connect("toggled", self.__toggle_concatenate)
        concatenate_btn.set_active(self.concatenate_titles)
        concatenate_btn.set_margin_start(10)
        concatenate_btn.set_margin_end(10)
        self.configs_list_box.append(concatenate_btn)

        self.configs_list_box.append(Gtk.Separator())
        concat_label = Gtk.Label(label="Concatenated title name template:")
        concat_label.set_margin_start(30)
        concat_label.set_margin_end(30)
        self.configs_list_box.append(concat_label)

        self.concatenated_title_name_text = Gtk.Text()
        self.concatenated_title_name_text.set_text(self.concatenated_title_name_template)
        self.configs_list_box.append(self.concatenated_title_name_text)

        self.configs_list_box.append(Gtk.Separator())

        output_dir_btn = Gtk.Button(label="Select output directory")
        output_dir_btn.connect("clicked", self.__select_output_dir)
        self.configs_list_box.append(output_dir_btn)

        self.configs_list_box.append(Gtk.Separator())

        self.configs_list_box.append(Gtk.Label(label="Selected Output directory:"))
        self.output_dir_label = Gtk.Label(label="None")
        self.configs_list_box.append(self.output_dir_label)

        self.configs_list_box.append(Gtk.Separator())

        self.configs_list_box.append(Gtk.Label(label="Video encoder:"))
        self.video_encoder_text = Gtk.Text()
        self.video_encoder_text.set_text(self.video_encoder)
        self.configs_list_box.append(self.video_encoder_text)

        self.configs_list_box.append(Gtk.Label(label="Quality:"))
        self.quality_text = Gtk.Text()
        self.quality_text.set_text(str(self.quality))
        self.configs_list_box.append(self.quality_text)

        self.configs_list_box.append(Gtk.Label(label="Encoder preset:"))
        self.encoder_preset_text = Gtk.Text()
        self.encoder_preset_text.set_text(self.encoder_preset)
        self.configs_list_box.append(self.encoder_preset_text)

        self.configs_list_box.append(Gtk.Label(label="Audio encoder:"))
        self.audio_encoder_text = Gtk.Text()
        self.audio_encoder_text.set_text(self.audio_encoder)
        self.configs_list_box.append(self.audio_encoder_text)

        self.configs_list_box.append(Gtk.Separator())

    def __toggle_keep_individual(self, btn):
        self.keep_individual_titles = btn.get_active()

    def __toggle_concatenate(self, btn):
        self.concatenate_titles = btn.get_active()

    def __select_output_dir(self, btn):
        dialog = Gtk.FileDialog(title="Select File Output Directory")

        dialog.open(parent=self.main_window, callback=self.__output_dir_selected)

    def __output_dir_selected(self, source_dialog, res):
        try:
            folder = source_dialog.open_finish(res).get_path()
            if not os.path.isdir(folder):
                folder = os.path.dirname(folder)

            print(f"Selected output folder: {folder}")

            self.output_dir = folder
            self.output_dir_label.set_text(folder)
        except Exception as e:
            pass

    def get_handbrake_options(self, title_data: Dict) -> List[str]:

        outfile = self.get_individual_title_name(title_data)

        args = [
            "-e", self.video_encoder_text.get_text(),
            "-q", str(float(self.quality_text.get_text())),
            "--encoder-preset", self.encoder_preset_text.get_text(),
            "-E", self.audio_encoder_text.get_text(),
            "-t", str(int(title_data['title_num'])),
            "--markers",
            "-i", f"{title_data['file_path']}",
            "-o", f"{outfile}"
        ]

        return args

    def get_ffmpeg_concat_options(self, titles: Dict) -> List[str]:
        if not self.concatenate_titles:
            return []

        if not titles:
            return []

        if len(titles) == 1:
            return []

        concat_option = "concat:"
        for title in titles.values():
            concat_option += f"{self.get_individual_title_name(title)}|"

        concat_option = concat_option[:-1]
        outfile = self.get_concat_file_name(titles[next(iter(titles))])

        return [
            "-i", concat_option,
            "-c", "copy",
            f"{outfile}"
        ]

    def get_individual_title_name(self, title_data: Dict) -> str:
        jinja_template = jinja2.Template(self.individual_title_name_text.get_text())
        return jinja_template.render(**title_data)

    def get_concat_file_name(self, title_data: Dict) -> str:
        jinja_template = jinja2.Template(self.concatenated_title_name_text.get_text())
        return jinja_template.render(**title_data)
