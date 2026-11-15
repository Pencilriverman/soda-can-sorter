"""Run on Windows using development Python. The release runs with an empty PATH."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile

with tempfile.TemporaryDirectory(prefix='AutoClip portability ') as temp:
    temp = Path(temp)
    with zipfile.ZipFile(sys.argv[1]) as archive:
        archive.extractall(temp)
    root = temp / 'GTA-AutoClip-Studio'
    root = root.rename(temp / 'Relocated Studio')
    env = dict(os.environ, PATH='', TEMP=str(temp), TMP=str(temp))
    for key in ('PYTHONHOME', 'PYTHONPATH'):
        env.pop(key, None)
    ff = root / 'runtime/ffmpeg/ffmpeg.exe'
    subprocess.run([ff, '-v', 'error', '-f', 'lavfi', '-i', 'testsrc2=size=320x180:rate=15',
                    '-f', 'lavfi', '-i', 'sine=frequency=440', '-t', '4',
                    '-c:v', 'libx264', '-c:a', 'aac', root / 'test input.mp4'], env=env, check=True)
    launcher = root / 'GTA-AutoClip.exe'
    state = root / 'runtime/studio.port'
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

    def request(route, payload=None, headers=None):
        req = urllib.request.Request(base + route, payload, headers or {})
        with opener.open(req, timeout=5) as response:
            return response.read()

    def launch():
        child = subprocess.Popen([launcher, '--no-browser'], env=env, cwd=temp)
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline and child.poll() is None:
            if state.is_file() and state.read_text().strip():
                return child, 'http://127.0.0.1:' + state.read_text().strip()
            time.sleep(0.15)
        child.kill()
        child.wait()
        diagnostics = root / 'startup-error.log'
        log = root / 'launcher.log'
        raise RuntimeError('\n'.join(file.read_text() for file in (diagnostics, log) if file.exists())
                           or 'Launcher did not become ready')

    def stop(child):
        subprocess.run([launcher, '--stop', '--no-browser'], env=env, cwd=temp, check=True, timeout=10)
        assert child.wait(timeout=30) == 0
        assert not state.exists()

    child, base = launch()
    try:
        assert b'GTA AutoClip Studio' in request('/')
        token = json.loads(request('/api/session'))['token']
        job_id = json.loads(request('/api/jobs', b'{"source":"test input.mp4"}',
                                    {'X-Studio-Token': token}))['id']
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            job = json.loads(request('/api/jobs'))[0]
            if job['status'] in ('done', 'failed'):
                break
            time.sleep(0.25)
        assert job['status'] == 'done', job
        clip = json.loads(job['result'])['clips'][0]
        video = root / 'data/clips' / clip['clip']
        assert video.stat().st_size > 1000
        probe = root / 'runtime/ffmpeg/ffprobe.exe'
        media = subprocess.check_output([probe, '-v', 'error', '-show_streams',
                                         '-of', 'json', video], env=env)
        streams = json.loads(media)['streams']
        assert (streams[0]['width'], streams[0]['height'], streams[0]['codec_name']) == (720, 1280, 'h264')
        assert any(stream['codec_type'] == 'audio' for stream in streams)
        assert request('/thumbnails/' + clip['thumbnail']).startswith(b'\xff\xd8')
        assert len(request('/clips/' + clip['clip'], headers={'Range': 'bytes=0-99'})) == 100
        print('Relocated ZIP, spaces in path, empty PATH, dashboard, offline rendering, thumbnails and media ranges passed. Encoder:', clip['encoder'])
    finally:
        stop(child)
    child, base = launch()
    try:
        assert json.loads(request('/api/jobs'))[0]['id'] == job_id
        assert request('/clips/' + clip['clip']) == video.read_bytes()
        print('Clean shutdown, restart, database persistence and MP4 export passed.')
    finally:
        stop(child)
