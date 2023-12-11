import requests
from tqdm import tqdm
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor
import re
import os

URL_TEMPLATE = "https://luna.loom.com/id/{}/rev/{}/resource/hls/{}"
POLICY = '?Policy={}&KeyPairId={}&Signature={}&Key-Pair-Id={}'

def download_chunk(url):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        return response.content
    else:
        return None

def download_chunks(loom_id, loom_rev, urls, output_file):
    urls = [URL_TEMPLATE.format(loom_id, loom_rev, url) + POLICY for url in urls]
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(download_chunk, url) for url in urls]
        chunks = [future.result() for future in tqdm(futures, total=len(urls), desc=f"Downloading {output_file}")]

    with open(output_file, 'wb') as output:
        for chunk in chunks:
            output.write(chunk)

def get_data(loom_id, loom_rev, tag):
    url = URL_TEMPLATE.format(loom_id, loom_rev, tag) + POLICY
    response = requests.get(url)
    response.raise_for_status()
    return [line for line in response.text.splitlines() if not line.startswith('#')]

def merge_audio_video(ffmpeg_path, audio_file, video_file, output_file):
    cmd = [
        ffmpeg_path,
        '-i', audio_file,
        '-i', video_file,
        '-c', 'copy',
        output_file
    ]
    subprocess.run(cmd)


if __name__ == "__main__":
    # Replace these URLs with your actual audio and video chunk URLs
    parser = argparse.ArgumentParser()
    parser.add_argument('--id', help='Loom video ID', required=True)
    parser.add_argument('--rev', help='Loom video revision')
    parser.add_argument('--ffmpeg_path', help='Path to ffmpeg binary', default='ffmpeg')
    args = parser.parse_args()

    response = requests.get(f"https://www.loom.com/share/{args.id}")
    if response.status_code != 200:
        print("Invalid Loom ID")
        exit(1)
    
    try:
        policy = re.search(r'"Policy":"([^"]+)"', response.text).group(1)
        key_pair_id = re.search(r'"KeyPairId":"([^"]+)"', response.text).group(1)
        signature = re.search(r'"Signature":"([^"]+)"', response.text).group(1)
        args.rev = re.search(r'"url":"([^"]+)"', response.text).group(1)
        args.rev = re.search(r'/rev/([^/]+)', args.rev).group(1)
        POLICY = POLICY.format(policy, key_pair_id, signature, key_pair_id)
    except AttributeError:
        print(f'Impossible to find policy, key_pair_id and signature for video {args.id}')
        exit(1)

    audio_urls = get_data(args.id, args.rev, 'mediaplaylist-audio.m3u8')
    video_bitrates = get_data(args.id, args.rev, 'playlist-multibitrate.m3u8')
    video_urls = get_data(args.id, args.rev, video_bitrates[-1])

    audio_output_filename = f"{args.id}_only_audio.ts"
    video_output_filename = f"{args.id}_only_video.ts"
    final_output_filename = f"{args.id}.mp4"

    if not os.path.exists(audio_output_filename):
        download_chunks(args.id, args.rev, audio_urls, audio_output_filename)
    if not os.path.exists(video_output_filename):
        download_chunks(args.id, args.rev, video_urls, video_output_filename)

    try:
        merge_audio_video(args.ffmpeg_path, audio_output_filename, video_output_filename, final_output_filename)
        print("Download and merge complete!")

        os.remove(audio_output_filename)
        os.remove(video_output_filename)
        print("Temporary files removed!")
    except Exception as e:
        print("Error while merging audio and video")
        exit(1)