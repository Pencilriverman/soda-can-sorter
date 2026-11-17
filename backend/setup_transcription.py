"""Install portable Whisper assets before the launcher starts Studio."""

import hashlib
import json
import msvcrt
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODEL_URL = 'https://huggingface.co/Systran/faster-whisper-large-v3/resolve/main/'
MODEL_FILES = {
    'config.json': 'a9306624f5ec14270a014b647e5c316b6e03a662c369758d1b90697a7b0655b9',
    'model.bin': '69f74147e3334731bc3a76048724833325d2ec74642fb52620eda87352e3d4f1',
    'preprocessor_config.json': '7ccc62c6f2765af1f3b46c00c9b5894426835a05021c8b9c01eecb6dfb542711',
    'tokenizer.json': '6d8cbd7cd0d8d5815e478dac67b85a26bbe77c1f5e0c6d76d1ce2abc0e5f21ca',
    'vocabulary.json': 'c69260f2ab26d659b7c398f9a2b2b48ed0df16c3b47d7326782fd9cba71690c1',
}
CUDA_PACKAGES = (
    ('nvidia-cublas-cu12', '12.6.4.1', '9e4fa264f4d8a4eb0cdbd34beadc029f453b3bafae02401e999cf3d5a5af75f8',
     ('cublas64_12.dll', 'cublasLt64_12.dll')),
    ('nvidia-cudnn-cu12', '9.5.1.17', 'd7af0f8a4f3b4b9dbb3122f2ef553b45694ed9c384d5a75bab197b8eefb79ab8',
     ('cudnn64_9.dll', 'cudnn_adv64_9.dll', 'cudnn_cnn64_9.dll', 'cudnn_engines_precompiled64_9.dll',
      'cudnn_engines_runtime_compiled64_9.dll', 'cudnn_graph64_9.dll', 'cudnn_heuristic64_9.dll', 'cudnn_ops64_9.dll')),
)


def download(url, destination, checksum):
    partial = destination.with_suffix(destination.suffix + '.part')
    print(f'Downloading {destination.name}…', flush=True)
    try:
        digest = hashlib.sha256()
        with urllib.request.urlopen(url, timeout=60) as response, partial.open('wb') as output:
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
                output.write(chunk)
        if digest.hexdigest() != checksum:
            raise ValueError(f'Checksum mismatch for {destination.name}.')
        partial.replace(destination)
    finally:
        partial.unlink(missing_ok=True)


def has_nvidia():
    tool = shutil.which('nvidia-smi.exe')
    if tool is None:
        return False
    try:
        return subprocess.run([tool, '-L'], capture_output=True, timeout=10).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def install_cuda(folder):
    folder.mkdir(parents=True, exist_ok=True)
    for package, version, checksum, dlls in CUDA_PACKAGES:
        if all((folder / name).is_file() for name in dlls):
            continue
        with urllib.request.urlopen(f'https://pypi.org/pypi/{package}/{version}/json', timeout=30) as response:
            files = json.load(response)['urls']
        wheel = next(file for file in files if file['filename'].endswith('-win_amd64.whl')
                     and file['digests']['sha256'] == checksum)
        archive = folder / wheel['filename']
        if not archive.exists():
            download(wheel['url'], archive, checksum)
        with zipfile.ZipFile(archive) as source:
            members = {Path(name).name: name for name in source.namelist() if name.endswith('.dll')}
            for name in dlls:
                temporary = folder / (name + '.part')
                with source.open(members[name]) as reader, temporary.open('wb') as writer:
                    shutil.copyfileobj(reader, writer)
                temporary.replace(folder / name)
        archive.unlink()


def main():
    model = ROOT / 'models/transcription/whisper-large-v3'
    model.mkdir(parents=True, exist_ok=True)
    with (model.parent / '.setup.lock').open('a+b') as lock:
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as error:
            raise RuntimeError('Whisper setup is already running in another window.') from error
        for filename, checksum in MODEL_FILES.items():
            destination = model / filename
            if not destination.is_file():
                download(MODEL_URL + filename, destination, checksum)
        if has_nvidia():
            install_cuda(ROOT / 'runtime/cuda')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, StopIteration, KeyError, zipfile.BadZipFile) as error:
        raise SystemExit(f'Could not finish transcription setup: {error}') from error
