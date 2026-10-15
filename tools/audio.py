"""Off Paper opening: music and sound design, synthesised from scratch.

No samples, loops or recordings are used. Every sound below is generated from
sine waves and seeded noise, so the track is original work with no third party
licence. Timing comes from the events file the video renderer writes, so the
sound lands on the picture.

usage: python3 audio.py events.json out.wav
"""
import json
import sys
import wave

import numpy as np

SR = 48000
rng = np.random.default_rng(36)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env_adsr(n, a, d, s, r, sus_len):
    """Attack, decay, sustain level, release, in seconds. sus_len is the hold time."""
    A, D, S_, R = int(a * SR), int(d * SR), int(sus_len * SR), int(r * SR)
    e = np.concatenate([
        np.linspace(0, 1, max(A, 1), endpoint=False) ** 2,
        np.linspace(1, s, max(D, 1), endpoint=False),
        np.full(max(S_, 0), s),
        s * np.linspace(1, 0, max(R, 1)) ** 2,
    ])
    out = np.zeros(n)
    out[:min(n, len(e))] = e[:n]
    return out


def place(buf, sig, t, pan=0.0, gain=1.0):
    i = int(t * SR)
    if i >= buf.shape[0]:
        return
    sig = sig[: buf.shape[0] - i] * gain
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * l
    buf[i:i + len(sig), 1] += sig * r


def soft_saw(f, dur, bright=6, detune=0.0):
    """Band limited saw made of harmonics, darker with fewer partials."""
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for k in range(1, bright + 1):
        if f * k > 9000:
            break
        out += np.sin(2 * np.pi * f * k * (1 + detune) * t + k) / k ** 1.4
    return out


def pad_chord(notes, dur, gain=0.09):
    n = int(dur * SR)
    sig = np.zeros((n, 2))
    for j, m in enumerate(notes):
        for side, det in ((0, -0.0025), (1, 0.0025)):
            v = soft_saw(midi(m), dur, bright=5, detune=det)
            sig[:, side] += v
    e = env_adsr(n, 0.9, 0.5, 0.85, 1.2, dur - 2.6)
    return sig * e[:, None] * gain / len(notes)


def pluck(f, dur=0.5, gain=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)
    return s * np.exp(-t * 9) * (1 - np.exp(-t * 400)) * gain


def bell(f, dur=2.5, gain=0.1):
    n = int(dur * SR)
    t = np.arange(n) / SR
    parts = [(1, 1, 2.2), (2.0, 0.45, 3.0), (3.01, 0.22, 4.5), (4.17, 0.12, 6.0)]
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * d) for r, a, d in parts)
    return s * (1 - np.exp(-t * 600)) * gain


def tick(f=3200, gain=0.05):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n) * np.exp(-t * 180)
    blip = np.sin(2 * np.pi * f * t) * np.exp(-t * 90)
    return (0.35 * noise + blip) * gain


def lock(f=900, gain=0.09):
    n = int(0.18 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * f * t) * np.exp(-t * 45) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t * 70)
    click = rng.standard_normal(n) * np.exp(-t * 600) * 0.4
    return (body + click) * gain


def thump(gain=0.25):
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 42 + 50 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * gain


def boom(gain=0.5, dur=3.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 38 + 60 * np.exp(-t * 12)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 1.6) * (1 - np.exp(-t * 300)) * gain


def riser(dur, gain=0.08):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    spec = np.fft.rfft(noise)
    freqs = np.fft.rfftfreq(n, 1 / SR)
    spec *= np.exp(-((freqs - 2500) / 2200) ** 2)
    s = np.fft.irfft(spec, n)
    s /= np.abs(s).max()
    return s * (t / dur) ** 2.5 * gain


def reverb(x, seconds=2.4, wet=0.22):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = np.zeros_like(x)
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-t * 3.2 / seconds * 2)
        ir[: int(0.012 * SR)] = 0
        ir /= np.sqrt((ir ** 2).sum())
        L = len(x) + n
        y = np.fft.irfft(np.fft.rfft(x[:, ch], L) * np.fft.rfft(ir, L), L)[: len(x)]
        out[:, ch] = y
    return x * (1 - wet) + out * wet * 2.2


def main(events_path, out_path):
    ev = json.load(open(events_path))
    T = ev["timeline"]
    dur = ev["duration"]
    N = int(dur * SR)
    mix = np.zeros((N, 2))

    # Harmony: D minor colour that resolves to D major as the name appears.
    bar = 2.5
    chords = [
        (0.0, [50, 57, 60, 64, 65]),     # Dm(add9)
        (bar, [46, 53, 57, 60, 62]),     # Bbmaj7(add9)
        (2 * bar, [43, 50, 53, 57, 58]), # Gm9
        (3 * bar, [45, 52, 55, 59, 62]), # A7sus4
    ]
    for start, notes in chords:
        place(mix, pad_chord(notes, bar + 1.2)[:, 0], start, -0.4, 1.0)
        place(mix, pad_chord(notes, bar + 1.2)[:, 1], start, 0.4, 1.0)
    final = [38, 50, 54, 57, 64, 66]     # D major add9, held under the name
    hold = T["fadeOut"][1] - T["collapse"][1]
    fin = pad_chord(final, hold + 0.4, gain=0.1)
    place(mix, fin[:, 0], T["collapse"][1], -0.4)
    place(mix, fin[:, 1], T["collapse"][1], 0.4)

    # Quiet eighth note arpeggio once the page starts to break up.
    beat = 0.3125
    arp = {0: [62, 65, 69, 72], 1: [58, 62, 65, 69], 2: [55, 58, 62, 65], 3: [57, 62, 64, 67]}
    t = T["scan"][0]
    i = 0
    while t < T["collapse"][1] - 0.05:
        ci = min(3, int(t // bar))
        note = arp[ci][i % 4] + (12 if i % 8 >= 4 else 0)
        g = 0.035 + 0.05 * min(1, (t - T["scan"][0]) / 5)
        place(mix, pluck(midi(note), gain=g), t, pan=0.5 * np.sin(i * 1.3))
        t += beat
        i += 1

    # Low heartbeat while the tiles travel and lock.
    t = T["fly"][0]
    while t < T["collapse"][1] - 0.2:
        place(mix, thump(0.16), t)
        t += 2 * beat

    # Scan: a fine tick as each ledger line turns into tiles.
    for k, ts in enumerate(ev["lineScan"]):
        place(mix, tick(2800 + 120 * k), ts, pan=-0.3 + 0.08 * k)

    # Lock: one click per completed ledger row, stepping up the scale.
    steps = [0, 2, 3, 5, 7, 9, 10, 12]
    for k, ts in enumerate(ev["rowLock"]):
        place(mix, lock(midi(74 + steps[k]) / 2), ts, pan=0.35)

    # Verification pulse: a soft bell run across the grid.
    run = [62, 64, 65, 67, 69, 72, 74, 76]
    p0, p1 = T["pulse"]
    for k, m in enumerate(run):
        place(mix, bell(midi(m), 1.6, 0.03), p0 + (p1 - p0 - 0.3) * k / 7, pan=-0.5 + k / 7)

    # Riser into the name, then the resolve.
    c0, c1 = T["collapse"]
    place(mix, riser(c1 - c0 + 0.05), c0)
    place(mix, boom(0.26), c1)
    for m, g in ((62, 0.07), (66, 0.05), (69, 0.05), (74, 0.04), (78, 0.03)):
        place(mix, bell(midi(m), 3.5, g), c1, pan=(m - 70) / 12)

    mix = reverb(mix)

    # Fade with the picture, then silence on the solid Slate end frame.
    f0, f1 = T["fadeOut"]
    tt = np.arange(N) / SR
    fade = np.clip((f1 + 0.2 - tt) / (f1 + 0.2 - f0), 0, 1) ** 1.5
    mix *= fade[:, None]
    fi = int(0.02 * SR)
    mix[:fi] *= np.linspace(0, 1, fi)[:, None]

    mix = np.tanh(mix * 1.2) / 1.2
    mix /= np.abs(mix).max() / 0.7
    pcm = (mix * 32767).astype("<i2")
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
