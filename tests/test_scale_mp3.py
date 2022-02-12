import pytest
from src.scale_mp3 import scale_mp3_file

mp3_files = [("", "", 44000, True), ("", "", 10000, True)]


pytest.mark.parametrize("input_file_path, output_file_path, expected_frequency, output_as_a_file", mp3_files)
def test_sclae_mp3(input_file_path, output_file_path, expected_frequency):
    # when
    scaled_mp3_file = scale_mp3_file(input_file_path=input_file_path, output_file_path=output_file_path, expected_frequency=expected_frequency)


    # Then
    assert scaled_mp3_file["frequency"] == expected_frequency
