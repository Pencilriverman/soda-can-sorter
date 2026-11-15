# Portability test results

Release 0.1.0, Windows x64, tested on the development PC.

| Check | Result |
| --- | --- |
| Build release folder, compile launcher, create ZIP | Passed |
| Extract ZIP and relocate to a different folder with spaces | Passed |
| Start from a working directory outside the application | Passed |
| Start with an empty PATH | Passed |
| Submit a local video with a relative path containing spaces | Passed |
| Analyze and rank candidates, render H.264 at 720 × 1280 with audio | Passed, NVENC |
| Serve dashboard, JPEG thumbnail, partial MP4 response and full MP4 export | Passed |
| Stop with the executable, restart, retrieve the previous job and clip | Passed |
| Different drive letter, removable media, second Windows PC | Pending |
| Visible browser launch, CPU fallback, YouTube downloads, external providers and upgrade rehearsal | Pending |

Run `python smoke.py dist/GTA-AutoClip-Studio-0.1.0-win-x64.zip` from the source directory. Set TEMP and TMP to a writable folder on another drive to exercise that location. The smoke test uses a synthetic four-second video and loopback HTTP. The development shell sandbox blocked loopback with WinError 10013. The smoke test passed when run with loopback access.

Bundled model inference, model packages, VRAM controls, GTA-specific detection, and the optional integrations remain outstanding. The current local scorer uses FFmpeg scene and audio measurements.
