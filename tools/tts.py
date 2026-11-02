# Builds a voiceover from a line-by-line script with Microsoft Edge neural voices.
# Each line is synthesised separately so we control the pauses; word times inside a line are
# estimated by character length (good enough for captions).
# Usage: python tools/tts.py <script.json> <audio-dir> <timeline.json>
# Needs: pip install edge-tts, and ffmpeg/ffprobe on PATH (or set FFMPEG/FFPROBE).
# script.json: {"voice": "...", "rate": "+8%", "lead": 0.2, "lines": [{"text": "...", "gap": 0.15}, ...]}
import asyncio, json, os, subprocess, sys
import edge_tts

FFPROBE = os.environ.get('FFPROBE', 'ffprobe')


FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')


def trim_silence(path):
    """Cut the voice service's leading/trailing silence, keeping a 40ms margin."""
    total = duration(path)
    log = subprocess.run([FFMPEG, '-hide_banner', '-i', path, '-af', 'silencedetect=noise=-40dB:d=0.08', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    starts = [float(l.split('silence_start: ')[1]) for l in log.splitlines() if 'silence_start' in l]
    ends = [float(l.split('silence_end: ')[1].split(' ')[0]) for l in log.splitlines() if 'silence_end' in l]
    head = ends[0] if starts and starts[0] < 0.01 and ends else 0.0
    tail = starts[-1] if starts and ends and ends[-1] >= total - 0.01 else total
    a, b = max(0.0, head - 0.04), min(total, tail + 0.04)
    trimmed = path.replace('.mp3', '.trim.mp3')
    subprocess.run([FFMPEG, '-v', 'error', '-y', '-i', path, '-ss', f'{a:.3f}', '-to', f'{b:.3f}', '-c:a', 'libmp3lame', '-q:a', '2', trimmed], check=True)
    os.replace(trimmed, path)


def duration(path):
    out = subprocess.run([FFPROBE, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


async def synth(text, path, voice, rate):
    # the service intermittently returns no audio under rapid requests; retry with backoff
    for attempt in range(8):
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(path)
            return
        except edge_tts.exceptions.NoAudioReceived:
            await asyncio.sleep(2 + attempt * 2)
    raise RuntimeError(f'no audio for: {text}')


def main(script_path, audio_dir, timeline_path):
    script = json.load(open(script_path, encoding='utf-8'))
    os.makedirs(audio_dir, exist_ok=True)
    t = script.get('lead', 0.2)
    timeline = []
    for i, line in enumerate(script['lines']):
        path = os.path.join(audio_dir, f'{i:02d}.mp3')
        asyncio.run(synth(line['text'], path, script['voice'], script['rate']))
        trim_silence(path)
        dur = duration(path)
        words, total = line['text'].split(), sum(len(w) + 1 for w in line['text'].split())
        acc, wt = 0, []
        for w in words:
            wt.append({'text': w, 'start': round(t + dur * acc / total, 3)})
            acc += len(w) + 1
        timeline.append({'file': f'{i:02d}.mp3', 'text': line['text'], 'start': round(t, 3), 'dur': round(dur, 3), 'words': wt})
        t += dur + line.get('gap', 0.15)
    json.dump({'total': round(t, 3), 'lines': timeline}, open(timeline_path, 'w', encoding='utf-8'), indent=1)
    print('total', round(t, 2))
    for l in timeline:
        print(f"{l['start']:6.2f} {l['dur']:5.2f}  {l['text']}")


if __name__ == '__main__':
    main(*sys.argv[1:])
