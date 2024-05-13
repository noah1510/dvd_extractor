import os.path
import subprocess
from typing import Dict, List


def execute_extraction(handbrake_params: Dict, ffmpeg_params: Dict, keep_individual_titles: bool, output_dir):
    print("Starting extraction")

    for title_num, params in handbrake_params.items():
        print(f"Title {title_num} Handbrake options: {params}")
        subprocess.run(["HandBrakeCLI", *params], cwd=output_dir)

    print(f"FFmpeg options: {ffmpeg_params}")
    if ffmpeg_params:
        with open(os.path.join(output_dir, ffmpeg_params['concat_file_name']), 'w') as f:
            f.write(ffmpeg_params['concat_file_str'])

        subprocess.run(["ffmpeg", *(ffmpeg_params['options'])], cwd=output_dir)

    if not keep_individual_titles:
        print("Deleting individual title files")
        for title_num, params in handbrake_params.items():
            subprocess.run(["rm", f"{params[-1]}"], cwd=output_dir)

    print("Extraction complete")
