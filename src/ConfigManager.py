import os
from typing import Dict, List

import jinja2
import gi

from src.TaskManager import Task
from src.TitleFinder import Title

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk


class HandbrakeExtractTask(Task):
    def __init__(self, title: Title, config_options: Dict, output_dir):
        super().__init__()

        self.title = title
        self.config_options = config_options
        if output_dir is None:
            self._cwd = os.path.dirname(title.path)
        else:
            self._cwd = output_dir

    def execute(self):
        title_dict = self.title.as_dict()
        outfile = jinja2.Template(self.config_options['individual_title_name_template']).render(**title_dict)

        args = [
            "-e", self.config_options['video_encoder'],
            "-q", str(float(self.config_options['quality'])),
            "--encoder-preset", self.config_options['encoder_preset'],
            "-E", self.config_options['audio_encoder'],
            "-t", str(int(title_dict['title_num'])),
            "--markers",
            "--all-audio",
            "--all-subtitles",
            str(self.config_options['handbrake_extra_options']),
            "-i", f"{title_dict['file_path']}",
            "-o", f"{outfile}"
        ]

        self._internal_execute(["HandBrakeCLI", *args])


class FFmpegConcatTask(Task):
    def __init__(self, titles: List[Title], config_options: Dict, output_dir):
        super().__init__()

        self.titles = titles
        self.config_options = config_options
        if output_dir is None:
            self._cwd = os.path.dirname(titles[0].path)
        else:
            self._cwd = output_dir

    def execute(self):
        concat_file_str = ''
        for title in self.titles:
            title_dict = title.as_dict()
            title_filename = jinja2.Template(self.config_options['individual_title_name_template']).render(**title_dict)
            concat_file_str += f"file '{title_filename}'\n"

        title_0 = self.titles[0]
        outfile = jinja2.Template(self.config_options['concatenated_title_name_template']).render(**title_0.as_dict())
        concat_file_name = f"{title_0.base_stem}.txt"

        with open(concat_file_name, 'w') as f:
            f.write(concat_file_str)

        args = [
            "-f", "concat",
            "-i", concat_file_name,
            "-c", "copy",
            f"{outfile}"
        ]

        self._internal_execute(["ffmpeg", *args])


class ConfigManager:
    def __init__(self, configs_list_box: Gtk.ListBox, main_window: Gtk.Window):
        self.configs_list_box = configs_list_box
        self.main_window = main_window

        self.keep_individual_titles = False
        self.concatenate_titles = True

        self.video_encoder = "svt_av1"
        self.quality = "32"
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

        self.configs_list_box.append(Gtk.Label(label="Extra Handbrake options:"))
        self.handbrake_options_text = Gtk.Text()
        self.handbrake_options_text.set_text("")
        self.configs_list_box.append(self.handbrake_options_text)

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

    def get_current_config(self) -> Dict:
        return {
            'keep_individual_titles': self.keep_individual_titles,
            'concatenate_titles': self.concatenate_titles,
            'video_encoder': self.video_encoder_text.get_text(),
            'quality': self.quality_text.get_text(),
            'encoder_preset': self.encoder_preset_text.get_text(),
            'audio_encoder': self.audio_encoder_text.get_text(),
            'output_dir': self.output_dir,
            'individual_title_name_template': self.individual_title_name_text.get_text(),
            'concatenated_title_name_template': self.concatenated_title_name_text.get_text(),
            'handbrake_extra_options': self.handbrake_options_text.get_text()
        }

    def get_handbrake_task(self, title_data: Title, output_dir=None) -> HandbrakeExtractTask:
        return HandbrakeExtractTask(title_data, self.get_current_config(), output_dir)

    def get_concat_task(self, titles: List[Title], output_dir=None) -> FFmpegConcatTask or None:
        if not self.concatenate_titles:
            return None

        if not titles:
            return None

        if len(titles) == 1:
            return None

        return FFmpegConcatTask(titles, self.get_current_config(), output_dir)
