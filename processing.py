"""Local-only FFmpeg processing. No networking or third-party Python dependencies."""
from pathlib import Path
from fractions import Fraction
import json, os, subprocess, sys, tempfile, logging, math

SPEEDS = tuple(round(i / 10, 1) for i in range(5, 16))
class LoopError(Exception): pass

def app_dir():
    return Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent

def tool(name):
    suffix = '.exe' if os.name == 'nt' else ''
    bundled = app_dir() / (name + suffix)
    if bundled.is_file(): return str(bundled)
    if not getattr(sys, 'frozen', False):
        import shutil
        found = shutil.which(name)
        if found: return found
    raise LoopError(f'{name} is missing. Please extract the complete LoopMaker folder again.')

def run(args):
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    result = subprocess.run(args, capture_output=True, creationflags=flags)
    if result.returncode:
        logging.error('%s', result.stderr.decode('utf-8', errors='replace')[-12000:])
        raise LoopError('This video could not be processed. Try another video or check the local log.')
    return result.stdout

def probe(path):
    try:
        data = json.loads(run([tool('ffprobe'), '-v', 'error', '-select_streams', 'v:0', '-show_streams', '-show_format', '-of', 'json', str(path)]))
        stream = data['streams'][0]
        duration = float(stream.get('duration') or data['format'].get('duration'))
        rate = float(Fraction(stream.get('avg_frame_rate', '0/1')))
        if not math.isfinite(duration) or duration <= 0: raise ValueError()
        if not math.isfinite(rate) or rate <= 0: rate = 30
        if duration > 10.000001: raise LoopError('Video must be 10 seconds or shorter.')
        return duration, rate
    except LoopError: raise
    except (ValueError, KeyError, IndexError, TypeError, ZeroDivisionError):
        raise LoopError('This file does not contain a readable video.')

def make_loop(source, speed):
    source = Path(source).resolve()
    if not source.is_file(): raise LoopError('Choose an existing video first.')
    if speed not in SPEEDS: raise LoopError('Choose a speed from 0.5x to 1.5x.')
    _, rate = probe(source)
    # Explicit CFR makes reverse/concat timestamps reliable, including VFR inputs.
    graph = (f'[0:v:0]setpts=PTS-STARTPTS,setpts=PTS/{speed},fps={rate:.10g},'
             'scale=trunc(iw/2)*2:trunc(ih/2)*2,setsar=1,split=2[f][r];'
             '[r]reverse,setpts=PTS-STARTPTS[rev];'
             '[f][rev]concat=n=2:v=1:a=0[out]')
    destination = source.parent / 'LoopMaker Output'
    try:
        destination.mkdir(exist_ok=True)
        stem = f'{source.stem}_LOOP_{speed:.1f}x'
        output = destination / (stem + '.mp4')
        index = 2
        while output.exists():
            output = destination / f'{stem}_{index}.mp4'
            index += 1
        # Work in a unique directory and publish only a successful complete output.
        with tempfile.TemporaryDirectory(prefix='.loopmaker-', dir=destination) as temp:
            partial = Path(temp) / 'loop.mp4'
            run([tool('ffmpeg'), '-hide_banner', '-loglevel', 'error', '-nostdin', '-i', str(source),
                 '-filter_complex', graph, '-map', '[out]', '-an', '-c:v', 'libx264', '-preset', 'veryfast',
                 '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-threads', '2', str(partial)])
            # Link creates atomically without overwriting a concurrently-created file.
            while True:
                try:
                    os.link(partial, output)
                    break
                except FileExistsError:
                    output = destination / f'{stem}_{index}.mp4'
                    index += 1
        return output
    except OSError as exc:
        logging.exception('Output failure')
        raise LoopError('Cannot save the loop beside this video. Move the video to a writable folder and try again.') from exc
