from ast import Bytes
from io import BytesIO
from typing import Optional, List, Union
import os
import uuid

import numpy as np
from pydub import AudioSegment
from scipy.io import wavfile
from scipy.signal import resample_poly, get_window, resample
import shutil


class ResamplerException(Exception):
    pass


class CannotExportWavFile(ResamplerException):
    pass


class CannotOpenMp3File(ResamplerException):
    pass


class Mp3Resampler:
    def __init__(
        self,
        input_file: Union[str, BytesIO],
        expected_sampling_rate: int,
        output_file_path: Optional[str],
    ):
        self._expected_sampling_rate = expected_sampling_rate
        self._output_file_path = output_file_path
        self._temp_folder = f"temp/{str(uuid.uuid4())}"
        os.mkdir(self._temp_folder)
        self._mp3_file_path = ""
        if isinstance(input_file, BytesIO):
            temp_file_name = str(uuid.uuid4()) + ".mp3"
            with open(f"{self._temp_folder}/{temp_file_name}", "wb") as fh:
                fh.writelines(input_file.readlines())

            self._mp3_file_path = f"{self._temp_folder}/{temp_file_name}"
        elif isinstance(input_file, str):
            self._mp3_file_path = input_file
        else:
            raise CannotOpenMp3File(
                f"Given input_file formats not recognized. Format: {type(input_file)}"
            )

    def _convert_mp3_to_wav(self) -> str:
        temp_converted_wav_file = f"{self._temp_folder}/{str(uuid.uuid4())}.wav"
        try:
            segment = AudioSegment.from_mp3(self._mp3_file_path)
            segment.export(temp_converted_wav_file, format="wav")
            return temp_converted_wav_file
        except Exception as e:
            raise CannotExportWavFile(f"There is an error occure:{str(e)}")

    def _resample_wav_file(self, window_size: int):
        temp_resampled_wav = f"{self._temp_folder}/{str(uuid.uuid4())}.wav"
        temp_wav_file_path = self._convert_mp3_to_wav()

        rate, data = wavfile.read(temp_wav_file_path)

        number_of_samples = round(
            len(data) * float(self._expected_sampling_rate) / rate
        )

        i_prev = 0
        resampled_data = np.empty(number_of_samples, dtype=np.float64)

        resampled_data = resample(
            data, number_of_samples, window=get_window("tukey", len(data))
        )

        wavfile.write(
            temp_resampled_wav,
            self._expected_sampling_rate,
            resampled_data.astype(np.int16),
        )

        return temp_resampled_wav

    def resample_mp3_file(self, window_size: int = 2048) -> BytesIO:
        temp_resampled_wav = self._resample_wav_file(window_size=window_size)
        temp_mp3_output = f"{self._temp_folder}/{str(uuid.uuid4())}.mp3"
        segment = AudioSegment.from_wav(temp_resampled_wav)
        if self._output_file_path:
            segment.export(self._output_file_path, format="mp3")
            with open(self._output_file_path, "rb") as fh:
                buffer = BytesIO(fh.read())
                # clean up tmp files
                self._clean_temp_files()
                return buffer

        else:
            segment.export(temp_mp3_output, format="mp3")
            with open(temp_mp3_output, "rb") as fh:
                buffer = BytesIO(fh.read())
                # clean up tmp files
                self._clean_temp_files()
                return buffer

    def _clean_temp_files(self):
        if os.path.isdir(self._temp_folder):
            shutil.rmtree(self._temp_folder)


# def resample_mp3_file(
#     input_file: Union[str, BytesIO],
#     expected_frequency: int,
#     output_file_path: Optional[str] = None,
# ) -> BytesIO:
#     """Resamples mp3 files

#     Args:
#         input_file_path (str): Input file path
#         expected_frequency (int): expected sampling rate
#         output_file_path (Optional[str], optional): if it will output file output file path. Defaults to None.

#     Raises:
#         NoPathGivenToSaveFile: [description]

#     Returns:
#         [BytesIO]: returns BytesIO buffer can be used to save as file for user
#     """

#     temp_file = "src/temp/tmp.wav"
#     temp_resampled_wav = "src/temp/tmp_resampled.wav"
#     temp_mp3_file = "src/temp/temp.mp3"
#     clean_temp_files([temp_file, temp_resampled_wav, temp_mp3_file])

#     rate, data = wavfile.read(temp_file)

#     number_of_samples = round(len(data) * float(expected_frequency) / rate)
#     i_prev = 0
#     resampled_data = np.empty([0, len(data)], dtype=np.float64)
#     for i in range(64, len(data), 512):
#         resampled_data[i:i_prev] = resample(
#             data[i_prev:i], number_of_samples, window=get_window("hann", 512)
#         )
#         i_prev = i

#     wavfile.write(
#         temp_resampled_wav, expected_frequency, resampled_data.astype(np.int16)
#     )

#     segment = AudioSegment.from_wav(temp_resampled_wav)
#     if output_file_path:
#         segment.set_frame_rate(expected_frequency)
#         segment.export(output_file_path, format="mp3")
#         with open(output_file_path, "rb") as fh:
#             buffer = BytesIO(fh.read())
#             # clean up tmp files
#             clean_temp_files([temp_file, temp_resampled_wav, temp_mp3_file])
#             return buffer

#     else:
#         segment.set_frame_rate(expected_frequency)
#         segment.export(temp_mp3_file, format="mp3")
#         with open(temp_mp3_file, "rb") as fh:
#             buffer = BytesIO(fh.read())
#             # clean up tmp files
#             clean_temp_files([temp_file, temp_resampled_wav, temp_mp3_file])
#             return buffer
