# Loom video downloader
## Installation
Install the dependencies through pip
```bash
pip install requests
pip install tqdm
```

### FFmpeg
The script uses FFmpeg to merge the video and audio streams. You can download FFmpeg from [here](https://ffmpeg.org/download.html). Make sure to add FFmpeg to your PATH.

Is it possible to download a precompiled version of FFmpeg from [here](https://github.com/BtbN/FFmpeg-Builds/releases). Make sure to download the `shared` version. One you have downloaded the zip file, extract it and add the `bin` folder to your PATH.

Another option is to specify the path to the FFmpeg executable using the `--ffmpeg_path` argument. For example:
```bash
python ./loom_downloader.py --id 5bbdeb480ba84e65b1b3de8c190e2003 --ffmpeg_path "D:\Downloads\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
```

## Usage
Provide the video id as the first argument of the script. The video id is the last part of the video url. For example, in the url `https://www.loom.com/share/5bbdeb480ba84e65b1b3de8c190e2003` the video id is `5bbdeb480ba84e65b1b3de8c190e2003`.
```bash
python ./loom_downloader.py --id 5bbdeb480ba84e65b1b3de8c190e2003
```
The script will download the video in the current directory with filename `{video_id}.mp4` which in this case is `5bbdeb480ba84e65b1b3de8c190e2003.mp4`.