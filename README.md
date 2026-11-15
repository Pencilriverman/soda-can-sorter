# GTA AutoClip Studio

Extract the ZIP to a writable directory on an x64 Windows 10/11 PC. Open `GTA-AutoClip.exe` or `Start.bat`. The launcher opens the dashboard on a loopback address. Enter a local video path or a YouTube URL and select **Generate Shorts**. The dashboard shows job status, previews, scores, and MP4 export links. Use **Stop Studio** or `Stop.bat` to shut down. A running job finishes before the process exits. Queued jobs interrupted by shutdown appear as failed on the next launch.

The offline analyzer ranks windows using scene changes and audio loudness. It renders letterboxed 720 × 1280 H.264 clips and JPEG thumbnails. This release uses heuristic ranking. GTA event recognition, model packages, and VRAM controls are pending. The optional providers in `config/models.json` can rerank selected windows through LM Studio, Ollama, or an OpenAI-compatible endpoint. Configure the model and URL before switching providers. External provider failures fall back to local scoring.

`config/settings.json` controls clip duration, maximum clips, encoder, and data directory. Relative storage paths resolve from the release folder. The default is `data`. Set the encoder to `cpu` to force software encoding. Automatic mode tries NVENC and falls back to x264 if encoding fails. NVENC requires a compatible NVIDIA GPU and driver. This release has no tested driver minimum. YouTube downloading requires network access and can fail when YouTube changes extraction requirements.

For startup issues, inspect `startup-error.log` and `launcher.log` next to the executable. For processing failures, check the job error in the dashboard. Confirm the entire archive was extracted and that the folder is writable. Use an absolute path for a local input outside the release folder or a relative path for input stored inside it.

## Build and update

Run `build.ps1 -PythonDir <python-directory> -MediaBin <binary-directory> -NodeDir <node-directory>` in PowerShell on the development PC. Supply the versions in DEPENDENCIES.md, including the license files. The build uses the Windows .NET Framework C# compiler and Windows tar. It produces a release directory and versioned ZIP under `dist`.

For a manual upgrade, stop Studio and wait for it to exit. Extract the new ZIP to a fresh directory. Copy your config, models, and data from the old folder. Keep the old folder intact for rollback. For external data, back up the database and data before starting the new version. SQLite uses schema versions and applies the initial migration at startup. A rollback should use the old data backup if a newer build has changed the schema.
