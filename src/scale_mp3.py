from ast import Bytes
from os import pathconf
from wave import Wave_write
from pydub import AudioSegment
from typing import Optional
from scipy.io import wavfile
import numpy as np
from scipy.signal import resample
from io import BytesIO

def scale_mp3_file(
    input_file_path: str,
    expected_frequency: int,
    output_file_path: Optional[str] = None,
    output_as_file: Optional[bool] = False,
):
    segment = AudioSegment.from_mp3(input_file_path)
    temp_file = "src/temp/tmp.wav"
    temp_resampled_wav = "src/temp/tmp_resampled.wav"
    temp_mp3_file = "src/temp/temp.mp3"
    segment.export(temp_file, format="wav")
    rate, data = wavfile.read(temp_file)

    # # in frequency domain
    # scale = rate/expected_frequency
    # fft_data = np.fft.fft(data)
    number_of_samples = round(len(data) * float(expected_frequency) / rate)
    resampled_data = resample(data, number_of_samples)
    # scaled_fft = fft_data *  scale
    
    # # data in time domain
    # data_in_td = np.fft.ifft(scaled_fft)
    wavfile.write(temp_resampled_wav, expected_frequency, resampled_data.astype(np.int16))
    
    segment = AudioSegment.from_wav(temp_resampled_wav)
    segment.export(temp_mp3_file, format="mp3")
    with open(temp_mp3_file, "rb") as fh:
        buffer = BytesIO(fh.read())
    return buffer

scale_mp3_file("tests/mp3_files_for_test/da0f4cd3-dcb0-40c4-b066-579063dd8994.mp3", 44000)
    
