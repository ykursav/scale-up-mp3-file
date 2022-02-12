from io import BufferedReader, BytesIO
from typing import Optional, List
import os

import numpy as np
from pydub import AudioSegment
from scipy.io import wavfile
from scipy.signal import resample


class ResamplerException(Exception):
    pass

class CannotExportWavFile(ResamplerException):
    pass

def resample_mp3_file(
    input_file_path: str,
    expected_frequency: int,
    output_file_path: Optional[str] = None,
) -> BytesIO:
    """Resamples mp3 files

    Args:
        input_file_path (str): Input file path
        expected_frequency (int): expected sampling rate
        output_file_path (Optional[str], optional): if it will output file output file path. Defaults to None.

    Raises:
        NoPathGivenToSaveFile: [description]

    Returns:
        [BytesIO]: returns BytesIO buffer can be used to save as file for user
    """

    temp_file = "src/temp/tmp.wav"
    temp_resampled_wav = "src/temp/tmp_resampled.wav"
    temp_mp3_file = "src/temp/temp.mp3"
    clean_temp_files([temp_file, temp_resampled_wav, temp_mp3_file])
    try:
        segment = AudioSegment.from_mp3(input_file_path)
        segment.export(temp_file, format="wav")
    except Exception as e:
        raise CannotExportWavFile(f"There is an error occure:{str(e)}")
    rate, data = wavfile.read(temp_file)

    number_of_samples = round(len(data) * float(expected_frequency) / rate)
    resampled_data = resample(data, number_of_samples)

    wavfile.write(
        temp_resampled_wav, expected_frequency, resampled_data.astype(np.int16)
    )
    segment = AudioSegment.from_wav(temp_resampled_wav)
    if output_file_path:
        segment.set_frame_rate(expected_frequency)
        segment.export(output_file_path, format="mp3")
        with open(output_file_path, "rb") as fh:
            buffer = BytesIO(fh.read())
             # clean up tmp files
            clean_temp_files([temp_file, temp_resampled_wav, temp_mp3_file])
            return buffer
       
    else:
        segment.set_frame_rate(expected_frequency)
        segment.export(temp_mp3_file, format="mp3")
        with open(temp_mp3_file, "rb") as fh:
            buffer = BytesIO(fh.read())
             # clean up tmp files
            clean_temp_files([temp_file, temp_resampled_wav, temp_mp3_file])
            return buffer

def clean_temp_files(list_of_path: List[str]):
    for path in list_of_path:
        if os.path.exists(path):
            os.remove(path)