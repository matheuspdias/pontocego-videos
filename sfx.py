"""
Efeitos sonoros sintetizados por código (sem bancos de som, sem direitos autorais).

Os sons são disparados automaticamente pelos eventos visuais registrados em engine.cue():
  anim:<tipo>  -> show(..., anim=...)       (pop, drop, stamp, up, left, right, fade)
  appear       -> boneco surgindo (figure(..., appear=t))
  arrow        -> arrow_draw
  key          -> cada letra de typewrite()
  transition   -> troca de cena
Sons extras podem ser listados no scenes.py:  SFX = [(t, "boom"), (t, "heartbeat"), ...]
Nomes disponíveis: pop, thud, swish, whoosh, dark_whoosh, impact, boom, key, click, ding,
                   shimmer, heartbeat, gust, riser, bell
"""
import numpy as np
from scipy.signal import lfilter, butter
import wave

SR = 44100
_rng = np.random.default_rng(42)


def _t(d):
    return np.arange(int(SR * d)) / SR


def _env(n, a=0.005, r=0.1):
    """attack linear + decaimento exponencial"""
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / max(r, 1e-4))
    return e


def _lp(x, f):
    b, a = butter(2, min(f, SR / 2 - 100) / (SR / 2), "low")
    return lfilter(b, a, x)


def _hp(x, f):
    b, a = butter(2, f / (SR / 2), "high")
    return lfilter(b, a, x)


def _bp(x, lo, hi):
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], "band")
    return lfilter(b, a, x)


def _sweep(f0, f1, d):
    t = _t(d)
    f = f0 * (f1 / f0) ** (t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def _noise(d):
    return _rng.standard_normal(int(SR * d))


def _norm(x, peak=1.0):
    m = np.max(np.abs(x)) or 1
    return x / m * peak


# ---------------------------------------------------------------- sons
def pop(pitch=1.0):
    d = 0.09
    x = _sweep(900 * pitch, 420 * pitch, d) * _env(int(SR * d), 0.002, 0.03)
    return _norm(x, 0.55)


def thud():
    d = 0.35
    x = _sweep(120, 45, d) * _env(int(SR * d), 0.002, 0.08)
    n = _lp(_noise(d), 900) * _env(int(SR * d), 0.001, 0.03)
    return _norm(x + 0.6 * n, 0.8)


def swish(d=0.28):
    n = _noise(d)
    t = _t(d)
    x = _bp(n, 1500, 7000) * np.sin(np.pi * t / d) ** 2
    return _norm(x, 0.22)


def whoosh(d=0.5):
    n = _noise(d)
    t = _t(d)
    lo = _lp(n, 1200)
    hi = _bp(n, 1200, 5000)
    k = t / d
    x = (lo * (1 - k) + hi * k) * np.sin(np.pi * k) ** 2
    return _norm(x, 0.30)


def dark_whoosh(d=1.1):
    n = _noise(d)
    t = _t(d)
    x = _lp(n, 500) * np.sin(np.pi * t / d) ** 1.5
    x += 0.4 * _sweep(70, 40, d) * np.sin(np.pi * t / d)
    return _norm(x, 0.40)


def impact():
    d = 1.4
    x = _sweep(80, 32, d) * _env(int(SR * d), 0.003, 0.35)
    n = _lp(_noise(d), 400) * _env(int(SR * d), 0.002, 0.25)
    c = _hp(_noise(0.03), 1500) * _env(int(SR * 0.03), 0.001, 0.008)
    x[: len(c)] += c * 0.5
    return _norm(x + 0.8 * n, 0.85)


def boom():
    d = 2.6
    x = _sweep(55, 28, d) * _env(int(SR * d), 0.01, 0.8)
    n = _lp(_noise(d), 220) * _env(int(SR * d), 0.01, 0.7)
    return _norm(x + n, 0.95)


def key():
    d = 0.035
    n = _bp(_noise(d), 1800, 6000) * _env(int(SR * d), 0.0005, 0.006)
    b = np.sin(2 * np.pi * _rng.uniform(140, 200) * _t(d)) * _env(int(SR * d), 0.001, 0.01)
    return _norm(n + 0.5 * b, _rng.uniform(0.18, 0.28))


def click():
    d = 0.02
    return _norm(_hp(_noise(d), 2500) * _env(int(SR * d), 0.0005, 0.004), 0.3)


def ding():
    d = 1.2
    t = _t(d)
    x = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((1320, 1), (2640, 0.4), (3960, 0.2)))
    return _norm(x * _env(len(t), 0.002, 0.3), 0.30)


def shimmer():
    d = 1.6
    t = _t(d)
    x = sum(np.sin(2 * np.pi * f * t) for f in (660, 990, 1485))
    e = np.minimum(1, t / 0.2) * np.exp(-t / 0.6)
    return _norm(x * e, 0.18)


def bell():
    d = 4.0
    t = _t(d)
    x = sum(a * np.sin(2 * np.pi * f * t) for f, a in ((220, 1), (440 * 1.19, 0.5), (660 * 1.33, 0.3), (880 * 1.5, 0.15)))
    return _norm(x * _env(len(t), 0.003, 1.2), 0.35)


def heartbeat():
    out = np.zeros(int(SR * 1.0))
    for st, amp in ((0.0, 1.0), (0.22, 0.7)):
        d = 0.18
        b = _sweep(70, 40, d) * _env(int(SR * d), 0.002, 0.05)
        i = int(st * SR)
        out[i:i + len(b)] += b * amp
    return _norm(_lp(out, 300), 0.7)


def gust(d=3.0):
    n = _noise(d)
    t = _t(d)
    x = _bp(n, 200, 1400) * np.sin(np.pi * t / d) ** 2 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.7 * t))
    return _norm(x, 0.35)


def riser(d=2.0):
    t = _t(d)
    x = _sweep(80, 600, d) * (t / d) ** 2 + _bp(_noise(d), 500, 4000) * (t / d) ** 3 * 0.5
    return _norm(x, 0.35)


SOUNDS = dict(pop=pop, thud=thud, swish=swish, whoosh=whoosh, dark_whoosh=dark_whoosh, impact=impact, boom=boom,
              key=key, click=click, ding=ding, shimmer=shimmer, bell=bell, heartbeat=heartbeat, gust=gust, riser=riser)


def ambience_dark(dur):
    """cama sonora sombria: grave contínuo + vento suave com variação lenta"""
    n = int(SR * dur)
    t = np.arange(n) / SR
    drone = (np.sin(2 * np.pi * 55 * t) + 0.7 * np.sin(2 * np.pi * 55.35 * t) + 0.4 * np.sin(2 * np.pi * 82.4 * t))
    drone *= 0.5 + 0.2 * np.sin(2 * np.pi * 0.05 * t)
    wind = _bp(_rng.standard_normal(n), 150, 900)
    wind *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t) * np.sin(2 * np.pi * 0.037 * t + 1)
    x = _norm(drone, 1) * 0.6 + _norm(wind, 1) * 0.4
    fade = np.minimum(1, t / 3.0) * np.minimum(1, (dur - t) / 3.0)
    return x * fade


# ---------------------------------------------------------------- mapeamento evento -> som
STYLE_LIGHT = {
    "anim:pop": lambda: pop(_rng.uniform(0.85, 1.25)),
    "anim:drop": thud,
    "anim:stamp": thud,
    "anim:up": swish, "anim:left": swish, "anim:right": swish,
    "appear": lambda: pop(0.7),
    "arrow": lambda: swish(0.22),
    "transition": whoosh,
    "key": key,
}
STYLE_DARK = {
    "anim:pop": lambda: _norm(_lp(pop(_rng.uniform(0.5, 0.7)), 1500), 0.35),
    "anim:drop": thud,
    "anim:stamp": impact,
    "anim:up": lambda: swish(0.4) * 0.6,
    "arrow": lambda: swish(0.3) * 0.6,
    "transition": dark_whoosh,
    "key": key,
}


def build_track(cues, dur, style="light", extra=(), ambience=None, sfx_gain=0.5, amb_gain=0.10):
    """cues: lista de (t, evento). extra: lista de (t, nome_do_som). Retorna np.array mono float."""
    table = STYLE_DARK if style == "dark" else STYLE_LIGHT
    n = int(SR * (dur + 3))
    out = np.zeros(n)
    last = {}
    for t0, ev in sorted(cues):
        if ev not in table or t0 < 0 or t0 > dur:
            continue
        gap = 0.04 if ev == "key" else 0.12
        if t0 - last.get(ev, -9) < gap:  # evita metralhadora de sons iguais
            continue
        last[ev] = t0
        s = table[ev]()
        i = int(t0 * SR)
        out[i:i + len(s)] += s[: n - i]
    for t0, name in extra:
        s = SOUNDS[name]()
        i = int(t0 * SR)
        out[i:i + len(s)] += s[: n - i]
    out = out[: int(SR * dur)] * sfx_gain
    if ambience == "dark":
        out += ambience_dark(dur) * amb_gain
    return np.clip(out, -1, 1)


def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(pcm.tobytes())
