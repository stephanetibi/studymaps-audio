#!/usr/bin/env python3
"""Genesis EN base-version audio (NaturalReader, Christopher, 200 WPM). 21 Nov 2026.
Usage: process_batch_EN.py <batch-number> <zip-path>
 1. copies the NaturalReader zip to ../sources/ (kept untouched)
 2. extracts each block as ../verses/Gen_EN_CC_VVV.mp3 (original 128 kbps file, renamed by the manifest)
 3. for every chapter whose verses are all present: trims each verse's lead/trail silence (-45 dB),
    joins them with 0.6 s silence (0.3 s at start, 0.6 s at end) into ../chapters/genesis_CC_EN.mp3
    (mono 44.1 kHz, 64 kbps) and writes ../timing/EN_CC.json {verse: {s, e}} (voice start/end, seconds).
"""
import csv, json, os, re, shutil, subprocess, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__)); EN = os.path.dirname(HERE)
SR, GAP, LEAD, TAIL, THR = 44100, 0.6, 0.3, 0.6, -45
b, zp = int(sys.argv[1]), sys.argv[2]
man = [r for r in csv.DictReader(open(os.path.join(HERE, 'batches/manifest_EN.csv'), encoding='utf-8')) if int(r['batch']) == b]
for d in ('sources', 'verses', 'chapters', 'timing'): os.makedirs(os.path.join(EN, d), exist_ok=True)
name = [f for f in os.listdir(os.path.join(HERE, 'batches')) if f.startswith(f'Gen_EN_B{b:02d}_')][0][:-4]
shutil.copy2(zp, os.path.join(EN, 'sources', name + '.zip'))
z = zipfile.ZipFile(zp); files = {}
for n in z.namelist():
    m = re.search(r'_(\d+)_[A-Za-z]+\.mp3$', n)
    if m: files[int(m.group(1))] = n
assert len(files) == len(man), f'zip has {len(files)} files, manifest {len(man)}'
chapters = set()
for r in man:
    c, v = int(r['chapter']), int(r['verse'])
    open(os.path.join(EN, 'verses', f'Gen_EN_{c:02d}_{v:03d}.mp3'), 'wb').write(z.read(files[int(r['line'])]))
    chapters.add(c)
allman = list(csv.DictReader(open(os.path.join(HERE, 'batches/manifest_EN.csv'), encoding='utf-8')))
def pcm(path):
    return subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
def trim(raw):
    import array; a = array.array('h', raw); lim = int(32768 * 10 ** (THR / 20)); win = int(SR * 0.01)
    loud = [i for i in range(0, len(a), win) if max(map(abs, a[i:i + win]), default=0) > lim]
    if not loud: return raw
    s0 = max(0, loud[0] - win); s1 = min(len(a), loud[-1] + 2 * win)
    return a[s0:s1].tobytes()
for c in sorted(chapters):
    vs = sorted(int(r['verse']) for r in allman if int(r['chapter']) == c)
    paths = [os.path.join(EN, 'verses', f'Gen_EN_{c:02d}_{v:03d}.mp3') for v in vs]
    if not all(os.path.exists(p) for p in paths): print('chapter', c, 'incomplete, later'); continue
    out = bytearray(b'\0\0' * int(SR * LEAD)); tim = {}
    for v, p in zip(vs, paths):
        t = trim(pcm(p)); s = len(out) / 2 / SR; out += t; e = len(out) / 2 / SR
        tim[str(v)] = {'s': round(s, 2), 'e': round(e, 2)}
        out += b'\0\0' * int(SR * (GAP if v != vs[-1] else TAIL))
    mp3 = os.path.join(EN, 'chapters', f'genesis_{c:02d}_EN.mp3')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '64k',
                    '-metadata', f'title=Genesis {c} (NAT English, base version)', '-metadata', 'artist=NaturalReader Christopher',
                    '-metadata', 'album=StudyMap Bible: Genesis EN', '-metadata', f'track={c}', mp3], input=bytes(out), check=True)
    json.dump({'lang': 'EN', 'book': 'genesis', 'chapter': c, 'source': 'NaturalReader commercial, voice Christopher, 200 WPM, NAT English (Genesis master v7)',
               'method': 'per-verse TTS files joined with 0.6 s silence; s/e = voice start/end', 'timing': tim},
              open(os.path.join(EN, 'timing', f'EN_{c:02d}.json'), 'w'), indent=1)
    print(f'chapter {c}: {len(vs)} verses, {len(out)/2/SR:.1f} s')
