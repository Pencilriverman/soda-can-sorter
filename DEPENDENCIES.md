# Runtime dependencies

| Component | Version | Source |
| --- | --- | --- |
| CPython AMD64 | 3.12.14 | Standard library, native DLLs, and MSVC runtime from the local Codex bundled Python distribution |
| FFmpeg and FFprobe x64 | 8.1.1 essentials | Gyan Windows builds, supplied as local files |
| yt-dlp x64 | 2026.10.26 | Standalone Windows executable, supplied as a local file |
| Node.js x64 | 24.19.0 | Bundled yt-dlp JavaScript challenge runtime |
| .NET Framework | CLR v4, Windows inbox | Windows Forms launcher |
| Browser | Windows default | Dashboard |

The backend imports only the Python standard library. The frontend has no third-party packages. Licenses supplied with the binary inputs are copied into their respective runtime directories. The release includes SHA-256 hashes for every runtime file. Rebuilds require matching input versions and can be compared against that inventory.
