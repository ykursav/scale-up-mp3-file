# scale-up-mp3-file

This repo is for scaling mp3 files.

# Installation

1. Please run below command in your linux.

```bash
sudo apt-get ffmpeg
```

2. Next step is installing dependencies.

```bash
pip install -r requirements.txt
```

3. If you want to run tests please install below requirements as well.

```bash
pip install -r requirements-dev.txt
```

4. Your code is ready to run.

# How to run the code

1. You can just import below code and it will be ready to run. You can give as input `path`of the file.

Function returns buffer. You can use or you can just give output_file_path. If outptut file path not given or `None`.
Then file will not be saved.

Example:

```python
from src.resample_mp3 import resample_mp3_file

resampled_mp3_file = resample_mp3_file(
        input_file_path=input_file_path,
        output_file_path=output_file_path,
        expected_frequency=expected_frequency,
    )
```
