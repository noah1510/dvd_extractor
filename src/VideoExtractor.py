import subprocess
from typing import Dict, List


def execute_extraction(handbrake_params: Dict, ffmpeg_params: List, keep_individual_titles: bool, output_dir):
    print("Starting extraction")

    for title_num, params in handbrake_params.items():
        print(f"Title {title_num} Handbrake options: {params}")
        subprocess.run(["HandBrakeCLI", *params], cwd=output_dir)

    print(f"FFmpeg options: {ffmpeg_params}")
    if ffmpeg_params:
        subprocess.run(["ffmpeg", *ffmpeg_params], cwd=output_dir)

    if not keep_individual_titles:
        print("Deleting individual title files")
        for title_num, params in handbrake_params.items():
            subprocess.run(["rm", f"{params[-1]}"], cwd=output_dir)

    print("Extraction complete")
