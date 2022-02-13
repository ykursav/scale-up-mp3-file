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
import subprocess


class ResamplerException(Exception):
    pass


class CannotExportWavFile(ResamplerException):
    pass


class CannotOpenMp3File(ResamplerException):
    pass


class CannotProcessFile(ResamplerException):
    pass


class Mp3Resampler:
    def __init__(
        self,
        input_file: Union[str, BytesIO],
        expected_sampling_rate: int,
        output_file_path: Optional[str],
    ):
        """MP3Resampler class with ffmpeg

        Args:
            input_file (Union[str, BytesIO]): Input File path or BytesIO buffer
            expected_sampling_rate (int): Expected sample rate
            output_file_path (Optional[str]): Output file path. If not given no file will be saved.

        Raises:
            CannotOpenMp3File: Incase of error due to opening mp3 file.
        """
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
        temp_mp3_output = f"{self._temp_folder}/{str(uuid.uuid4())}.mp3"
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    self._mp3_file_path,
                    "-ar",
                    str(self._expected_sampling_rate),
                    temp_mp3_output,
                ]
            )
        except Exception as e:
            raise CannotProcessFile(f"File cannot be proceed due to: {str(e)}")

        if self._output_file_path:
            if os.path.isfile(temp_mp3_output):
                shutil.copy(temp_mp3_output, self._output_file_path)
            with open(temp_mp3_output, "rb") as fh:
                buffer = BytesIO(fh.read())
                # clean up tmp files
                self._clean_temp_files()
                return buffer

        else:
            with open(temp_mp3_output, "rb") as fh:
                buffer = BytesIO(fh.read())
                # clean up tmp files
                self._clean_temp_files()
                return buffer

    def _clean_temp_files(self):
        if os.path.isdir(self._temp_folder):
            shutil.rmtree(self._temp_folder)
