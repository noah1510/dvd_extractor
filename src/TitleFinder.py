import os.path
from typing import Dict

import dvdread


class Title:
    def __init__(self, **kwargs):
        self.TitleNum = kwargs.get('TitleNum')
        self.NumberOfAngles = kwargs.get('NumberOfAngles')
        self.NumberOfAudios = kwargs.get('NumberOfAudios')
        self.NumberOfChapters = kwargs.get('NumberOfChapters')
        self.NumberOfSubpictures = kwargs.get('NumberOfSubpictures')
        self.PlaybackTimeFancy = kwargs.get('PlaybackTimeFancy')

        self.path = kwargs.get('path')
        self.base_stem = os.path.splitext(os.path.basename(self.path))[0]

    def print_title_info(self):
        print(
            f"Title {self.TitleNum} has {self.NumberOfAngles} angles, {self.NumberOfAudios} audio tracks, "
            f"{self.NumberOfChapters} chapters, {self.NumberOfSubpictures} subpictures, "
            f"and runs for {self.PlaybackTimeFancy}"
        )

    def as_dict(self) -> Dict:
        return {
            'title_num': self.TitleNum,
            'number_of_angles': self.NumberOfAngles,
            'number_of_audios': self.NumberOfAudios,
            'number_of_chapters': self.NumberOfChapters,
            'number_of_subpictures': self.NumberOfSubpictures,
            'playback_time_fancy': self.PlaybackTimeFancy,
            'file_path': self.path,
            'base_stem': self.base_stem
        }

    @staticmethod
    def get_all_titles(path):
        if not path:
            raise ValueError("No path provided")

        if not os.path.exists(path):
            raise FileNotFoundError("Path does not exist")

        dvd = dvdread.DVD(path)
        dvd.Open()

        print(f"Number of titles on disc: {dvd.NumberOfTitles}")

        title_list = dvd.get_all_titles()
        title_objects = {}
        for title in title_list:
            title_objects[title.TitleNum] = Title(
                TitleNum=title.TitleNum,
                NumberOfAngles=title.NumberOfAngles,
                NumberOfAudios=title.NumberOfAudios,
                NumberOfChapters=title.NumberOfChapters,
                NumberOfSubpictures=title.NumberOfSubpictures,
                PlaybackTimeFancy=title.PlaybackTimeFancy,
                path=path
            )

        dvd.Close()

        return title_objects
