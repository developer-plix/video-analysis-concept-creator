#!/usr/bin/env python3
"""
transcribe_video.py — Download a video from Google Drive (or any yt-dlp-supported URL)
and transcribe it using OpenAI Whisper.

Usage:
    python transcribe_video.py --url "<url>" --output /tmp/transcript.txt [--model base]

Requirements (install before running):
    pip install openai-whisper yt-dlp gdown --break-system-packages -q
"""

import argparse
import os
import sys
import tempfile
import subprocess

def download_video(url: str, output_path: str) -> str:
    """Download video from Google Drive or other URL using yt-dlp or gdown."""
    # Detect Google Drive links
    is_gdrive = "drive.google.com" in url or "docs.google.com" in url

    if is_gdrive:
        # Extract file ID from Google Drive URL
        import re
        file_id = None
        patterns = [
            r"/file/d/([a-zA-Z0-9_-]+)",
            r"id=([a-zA-Z0-9_-]+)",
            r"/d/([a-zA-Z0-9_-]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                file_id = match.group(1)
                break

        if not file_id:
            print(f"ERROR: Could not extract file ID from Google Drive URL: {url}", file=sys.stderr)
            sys.exit(1)

        print(f"Downloading from Google Drive (file ID: {file_id})...")
        try:
            import gdown
            gdown.download(id=file_id, output=output_path, quiet=False)
        except Exception as e:
            print(f"gdown failed: {e}. Trying yt-dlp fallback...", file=sys.stderr)
            result = subprocess.run(
                ["yt-dlp", "-o", output_path, url],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"yt-dlp also failed: {result.stderr}", file=sys.stderr)
                sys.exit(1)
    else:
        print(f"Downloading via yt-dlp: {url}")
        result = subprocess.run(
            ["yt-dlp", "-o", output_path, "--format", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best", url],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"yt-dlp failed: {result.stderr}", file=sys.stderr)
            sys.exit(1)

    if not os.path.exists(output_path):
        # yt-dlp may have added an extension
        for ext in [".mp4", ".mkv", ".webm", ".mov", ".m4a", ".mp3"]:
            candidate = output_path + ext
            if os.path.exists(candidate):
                return candidate
        print("ERROR: Downloaded file not found.", file=sys.stderr)
        sys.exit(1)

    return output_path


def transcribe(video_path: str, model_name: str = "base") -> str:
    """Transcribe audio from a video file using Whisper."""
    try:
        import whisper
    except ImportError:
        print("ERROR: openai-whisper not installed. Run: pip install openai-whisper --break-system-packages", file=sys.stderr)
        sys.exit(1)

    print(f"Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)

    print(f"Transcribing: {video_path}")
    result = model.transcribe(video_path, verbose=False)
    return result["text"].strip()


def main():
    parser = argparse.ArgumentParser(description="Download and transcribe a video.")
    parser.add_argument("--url", required=True, help="Video URL (Google Drive, Instagram, YouTube, etc.)")
    parser.add_argument("--output", required=True, help="Output path for the transcript text file")
    parser.add_argument("--model", default="base", choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: base). Use 'small' for better accuracy.")
    parser.add_argument("--keep-video", action="store_true", help="Keep the downloaded video file after transcription")
    args = parser.parse_args()

    # Use a temp file for the video
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        video_path = tmp.name

    try:
        # Download
        actual_video_path = download_video(args.url, video_path)

        # Transcribe
        transcript = transcribe(actual_video_path, args.model)

        # Save transcript
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(transcript)

        print(f"\n✅ Transcript saved to: {args.output}")
        print(f"\n--- Preview (first 300 chars) ---\n{transcript[:300]}...")

    finally:
        # Clean up video unless --keep-video
        if not args.keep_video:
            for path in [video_path, actual_video_path if 'actual_video_path' in dir() else None]:
                if path and os.path.exists(path) and path != args.output:
                    try:
                        os.remove(path)
                    except Exception:
                        pass


if __name__ == "__main__":
    main()
