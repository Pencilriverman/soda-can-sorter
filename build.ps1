param(
    [Parameter(Mandatory)][string]$PythonDir,
    [Parameter(Mandatory)][string]$MediaBin,
    [Parameter(Mandatory)][string]$NodeDir,
    [string]$OutputDir = (Join-Path $PSScriptRoot 'dist')
)
$ErrorActionPreference = 'Stop'
$PythonDir = (Resolve-Path -LiteralPath $PythonDir).Path
$MediaBin = (Resolve-Path -LiteralPath $MediaBin).Path
$NodeDir = (Resolve-Path -LiteralPath $NodeDir).Path
if ((& (Join-Path $NodeDir 'node.exe') --version) -ne 'v24.19.0') { throw 'Expected Node.js 24.19.0.' }
$release = Join-Path $OutputDir 'GTA-AutoClip-Studio'
if (Test-Path -LiteralPath $release) { throw "Move the previous build folder before rebuilding: $release" }
$python = Join-Path $PythonDir 'python.exe'
$yt = Join-Path $MediaBin 'yt-dlp.exe'
if ((& $python -I -c 'import platform; print(platform.python_version(), platform.machine())') -ne '3.12.14 AMD64') { throw 'Expected Python 3.12.14 AMD64.' }
foreach ($binary in 'ffmpeg','ffprobe') {
    if ((& (Join-Path $MediaBin "$binary.exe") -version | Select-Object -First 1) -notmatch "^$binary version 8\.1\.1-essentials_build-www\.gyan\.dev ") { throw "Unexpected $binary build." }
}
if ((& $yt --version) -ne '2026.10.26') { throw 'Expected yt-dlp 2026.10.26.' }
foreach ($folder in 'config','runtime/python','runtime/ffmpeg','runtime/yt-dlp','runtime/node','runtime/backend','frontend/dist','models/audio','models/vision','models/transcription') {
    New-Item -ItemType Directory -Path (Join-Path $release $folder) -Force | Out-Null
}
foreach ($name in 'python.exe','python3.dll','python312.dll','vcruntime140.dll','vcruntime140_1.dll','LICENSE.txt','DLLs') {
    Copy-Item -LiteralPath (Join-Path $PythonDir $name) -Destination "$release/runtime/python" -Recurse
}
New-Item -ItemType Directory -Path "$release/runtime/python/Lib" | Out-Null
Get-ChildItem -LiteralPath "$PythonDir/Lib" -Exclude 'site-packages','__pycache__','ensurepip' |
    Copy-Item -Destination "$release/runtime/python/Lib" -Recurse
foreach ($name in 'ffmpeg.exe','ffprobe.exe','ffmpeg-license.txt') { Copy-Item -LiteralPath (Join-Path $MediaBin $name) -Destination "$release/runtime/ffmpeg" }
foreach ($name in 'yt-dlp.exe','yt-dlp-LICENSE.txt') { Copy-Item -LiteralPath (Join-Path $MediaBin $name) -Destination "$release/runtime/yt-dlp" }
Copy-Item "$PSScriptRoot/config/*.json" "$release/config"
foreach ($name in 'node.exe','LICENSE') { Copy-Item -LiteralPath (Join-Path $NodeDir $name) -Destination "$release/runtime/node" }
Copy-Item "$PSScriptRoot/backend/studio.py","$PSScriptRoot/backend/setup_transcription.py" "$release/runtime/backend"
if (-not (Test-Path "$PythonDir/Lib/site-packages/faster_whisper")) { throw 'Install faster-whisper into the supplied Python environment before building.' }
Copy-Item "$PythonDir/Lib/site-packages" "$release/runtime/python/Lib" -Recurse
Copy-Item "$PSScriptRoot/frontend/index.html" "$release/frontend/dist"
Copy-Item "$PSScriptRoot/frontend/fonts" "$release/frontend/dist" -Recurse
Copy-Item "$PSScriptRoot/frontend/manual*" "$release/frontend/dist"
foreach ($name in 'README.md','Start.bat','Stop.bat','VERSION','DEPENDENCIES.md') { Copy-Item -LiteralPath (Join-Path $PSScriptRoot $name) -Destination $release }
$csc = Join-Path $env:WINDIR 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
$launcher = Join-Path $release 'GTA-AutoClip.exe'
$source = Join-Path $PSScriptRoot 'launcher\Launcher.cs'
& $csc /nologo /target:winexe /platform:x64 /optimize+ /reference:System.Windows.Forms.dll "/out:$launcher" $source
if ($LASTEXITCODE -ne 0) { throw 'Launcher compilation failed.' }
Get-ChildItem -LiteralPath "$release/runtime" -Recurse -File | Sort-Object FullName | ForEach-Object {
    '{0}  {1}' -f (Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant(), $_.FullName.Substring($release.Length + 1).Replace('\','/')
} | Set-Content -LiteralPath "$release/runtime-sha256.txt" -Encoding ascii
$version = (Get-Content -LiteralPath "$release/VERSION" -Raw).Trim()
$zip = Join-Path $OutputDir "GTA-AutoClip-Studio-$version-win-x64.zip"
if (Test-Path -LiteralPath $zip) { throw "Archive already exists: $zip" }
& "$env:WINDIR/System32/tar.exe" -a -cf $zip -C (Split-Path $release) (Split-Path $release -Leaf)
if ($LASTEXITCODE -ne 0) { throw 'ZIP creation failed.' }
Write-Output $zip
