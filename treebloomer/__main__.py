import logging
from pathlib import Path
from typing import List, Optional
import argparse

from treebloomer.processes.audio_extraction import extract_audio
from treebloomer.processes.audio_compression import compress_audio
from treebloomer.processes.transcript_extraction import extract_transcript
from treebloomer.processes.summarization import summarize_transcript
from treebloomer.processes.html_page_generation import generate_html_summary
from treebloomer.processes.word_cloud_generation import generate_word_cloud

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)d - %(message)s'
)

logger = logging.getLogger(__name__)

def is_excluded(file_path: Path, exclude: Optional[List[str]] = None) -> bool:
    if exclude is None:
        return False
    return any(ex in file_path.parts for ex in exclude) or file_path.name in exclude

def process_video_file(video_file: Path, exclude: Optional[List[str]] = None):
    logger.info(f"Processing {video_file}")
    subfolder = video_file.parent / video_file.stem
    subfolder.mkdir(exist_ok=True)

    try:
        audio_file = extract_audio(video_file, subfolder)
        compressed_audio = compress_audio(audio_file, subfolder)
        transcript_file = extract_transcript(compressed_audio, subfolder)
        summary_file = summarize_transcript(transcript_file, subfolder)
        wordcloud_file = generate_word_cloud(transcript_file, subfolder)
        html_summary_file = generate_html_summary(summary_file, subfolder)
    except Exception as e:
        logger.error(f"Failed to process {video_file}: {e}")

def main():
    default_directory_path = r"./input"
    parser = argparse.ArgumentParser(description="Process video files to extract audio and transcripts.")
    parser.add_argument("directory", nargs="?", default=default_directory_path, help="Directory containing video files to process")
    parser.add_argument("--exclude", nargs="*", default=None, help="Files or folders to exclude")

    args = parser.parse_args()
    directory = args.directory
    exclude = args.exclude

    logger.info(f"Processing video files in {directory}, excluding {exclude}")
    path = Path(directory)

    for video_file in path.rglob('*.mp4'):
        logger.info(f"Found video file: {video_file}")
        if not is_excluded(video_file, exclude):
            logger.info(f"Processing {video_file}...")
            process_video_file(video_file, exclude)
        else:
            logger.info(f"{video_file} is excluded, skipping...")

    print("Done!")

if __name__ == "__main__":
    main()
