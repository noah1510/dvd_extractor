import os.path
from typing import Dict, Any

import dvdread


class DvdManager:
    def __init__(self, path):
        if not path:
            raise ValueError("No path provided")

        if not os.path.exists(path):
            raise FileNotFoundError("Path does not exist")

        self.path = path

        self._dvd = dvdread.DVD(self.path)
        self._dvd.Open()

        print(f"Number of titles on disc: {self._dvd.NumberOfTitles}")

        self._titleList = self._dvd.get_all_titles().copy()

    def __del__(self):
        try:
            self._dvd.Close()
        except Exception:
            pass

        print("DVD closed")

    def get_title_list(self):
        return self._titleList

    def print_title_info(self):
        for title in self._titleList:
            print(
                f"Title {title.TitleNum} has {title.NumberOfAngles} angles, {title.NumberOfAudios} audio tracks, "
                f"{title.NumberOfChapters} chapters, {title.NumberOfSubpictures} subpictures, "
                f"and runs for {title.PlaybackTimeFancy}"
            )

    def create_title_dict(self, title_num) -> Dict[str, Any]:
        title = None
        for t in self._titleList:
            if t.TitleNum == title_num:
                title = t
                break

        if not title:
            raise ValueError(f"Title {title_num} not found")

        title_data = {
            'title_num': title.TitleNum,
            'title_length': title.PlaybackTimeFancy,
            'file_path': os.path.abspath(self.path),
            'base_stem': os.path.splitext(os.path.basename(self.path))[0],
        }

        return title_data
