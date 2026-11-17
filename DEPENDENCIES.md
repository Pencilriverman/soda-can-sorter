# Runtime dependencies

| Component | Version | Source |
| --- | --- | --- |
| CPython AMD64 | 3.12.14 | Standard library, native DLLs, and MSVC runtime from the local Codex bundled Python distribution |
| FFmpeg and FFprobe x64 | 8.1.1 essentials | Gyan Windows builds, supplied as local files |
| yt-dlp x64 | 2026.10.26 | Standalone Windows executable, supplied as a local file |
| Node.js x64 | 24.19.0 | Bundled yt-dlp JavaScript challenge runtime |
| .NET Framework | CLR v4, Windows inbox | Windows Forms launcher |
| Browser | Windows default | Dashboard |

The Python runtime for a build must include faster-whisper and its dependencies in `Lib/site-packages`. On first launch, Studio downloads the CTranslate2 Whisper Large v3 weights and, on NVIDIA PCs, the Windows cuBLAS 12 and cuDNN 9 libraries. The setup script checks the SHA-256 hashes before installing them inside the portable folder.
