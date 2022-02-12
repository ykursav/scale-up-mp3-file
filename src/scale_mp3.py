from os import pathconf
from pydub import AudioSegment
from typing import Optional

def scale_mp3_file(input_file_path: str, expected_frequency: int, output_file_path: Optional[str] = None, output_as_file: Optional[bool]=False):
    pass