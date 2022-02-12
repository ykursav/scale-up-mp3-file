from io import BufferedReader, BytesIO

import pytest
from pydub.audio_segment import AudioSegment
from pydub.utils import mediainfo
from scipy.io import wavfile

from src.resample_mp3 import resample_mp3_file

mp3_files = [
    ("tests/mp3_files_for_test/54f42f2314aab75c7a83f16d3c251e5f.mp3", None, 32000),
    ("tests/mp3_files_for_test/99559e12-f1c1-4b05-9255-24478b2cc96c.mp3", None, 44100),
    ("tests/mp3_files_for_test/c8262420-1406-4908-91f8-b9f17bd8df4a.mp3", None, 48000),
    ("tests/mp3_files_for_test/da0f4cd3-dcb0-40c4-b066-579063dd8994.mp3", None, 8000),
    ("tests/mp3_files_for_test/fb51e967a69615574eebe1f9d3b893a1.mp3", None, 12000),
]


@pytest.mark.parametrize(
    "input_file_path, output_file_path, expected_frequency", mp3_files
)
def test_resample_mp3_file(input_file_path, output_file_path, expected_frequency):
    # when
    resampled_mp3_file = resample_mp3_file(
        input_file_path=input_file_path,
        output_file_path=output_file_path,
        expected_frequency=expected_frequency,
    )

    # Then
    assert expected_frequency == get_sampling_rate(resampled_mp3_file)


def get_sampling_rate(file: BytesIO):
    temp_file_path = "tests/temp/tmp.mp3"
    f = open(temp_file_path, "wb")
    f.writelines(file.readlines())
    f.close()
    info = mediainfo(temp_file_path)

    return int(info["sample_rate"])
