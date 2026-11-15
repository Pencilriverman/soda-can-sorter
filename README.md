# YouTube Clip Studio

Portable Windows app for turning long videos into vertical Shorts. Paste a link, search YouTube, or use a local video path. Studio supports Most Replayed, Action, AI Transcript, AI Ranking, and Split into parts.

## Test the portable build

1. Download the Windows ZIP from Releases and extract the whole folder to a writable location.
2. Open `Start.bat`. Studio opens in your browser on port 57286.
3. Open **Instructions manual** in Studio for the illustrated walkthrough. For a first run without an AI provider, set AI Transcript to 0 and try Action.

The portable test build includes Python, FFmpeg, Node.js, and yt-dlp. AI Transcript and AI Ranking need timed captions and a configured language model. The optional Whisper model and CUDA bundle are separate from the test ZIP. Studio can use subtitle tracks when available.

Studio writes jobs and media into `data` inside the extracted folder. Use `Stop.bat` to shut it down. The launcher also listens on the local network. Use it on a trusted network and keep port 57286 off the public internet.

## Build from source

Run `build.ps1 -PythonDir <python-directory> -MediaBin <binary-directory> -NodeDir <node-directory>` in PowerShell on Windows. See [Dependencies](DEPENDENCIES.md) for the required versions and license files.

If startup fails, check `startup-error.log` and `launcher.log` beside the executable. Keep your old folder when upgrading so you have a backup of the job database, presets, and media.
