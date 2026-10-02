"""
Renderizador de vídeos do canal Ponto Cego (estilo sombrio desenhado).

Uso:
  python render.py stills <scenes.py> <pasta_saida> <t1> <t2> ...   # quadros de prévia (PNG)
  python render.py sheet  <scenes.py> <saida.png>   <t1> <t2> ...   # prévia em grade (contact sheet)
  python render.py build  <scenes.py> <audio.mp3>   <saida.mp4>     # vídeo final (paralelo + áudio + compressão)
"""
import sys, os, subprocess, importlib.util, tempfile, numpy as np
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *

XF = 0.28  # duração do crossfade entre cenas (s)


def load_module(path):
    spec = importlib.util.spec_from_file_location("scenes_mod", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_scenes(path):
    return load_module(path).SCENES


SFX_STYLE = "dark"
SFX_AMBIENCE = "dark"


def make_sfx(scenes_path, dur, out_wav):
    """roda cada cena no seu último instante para coletar os eventos visuais e sintetiza a trilha de efeitos"""
    import engine, sfx
    m = load_module(scenes_path)
    S = m.SCENES
    engine._CUES = []
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, 32, 32); c = cairo.Context(surf)
    for i, (st, en, fn) in enumerate(S):
        fn(c, min(en, dur) - 0.001)
        if i > 0:
            engine._CUES.append((st, "transition"))
    cues = engine._CUES
    engine._CUES = None
    if getattr(m, "SFX_OFF", False):
        cues = []
    track = sfx.build_track(cues, dur, getattr(m, "SFX_STYLE", SFX_STYLE), getattr(m, "SFX", ()),
                            getattr(m, "AMBIENCE", SFX_AMBIENCE), getattr(m, "SFX_GAIN", 0.5))
    sfx.write_wav(out_wav, track)
    peak = float(np.max(np.abs(track))) or 1e-6
    return len(cues), 20 * np.log10(peak)


def mix_graph(vol):
    """narração + efeitos em float (nunca deixe o ffmpeg negociar formato: 8 bits gera chiado na voz)"""
    f = "aformat=sample_fmts=fltp,aresample=48000,pan=stereo|c0=c0|c1=c0"
    return f"[1:a]{f}[n];[2:a]{f},volume={vol:.4f}[s];[n][s]amix=inputs=2:normalize=0:duration=first[a]"


def remix(scenes_path, audio, video_in, out_mp4, abr="160k"):
    """refaz só o áudio (narração + efeitos) de um vídeo já renderizado, copiando a imagem"""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio],
                               capture_output=True, text=True).stdout)
    tmp = tempfile.mkdtemp()
    sfx_wav = f"{tmp}/sfx.wav"
    ncues, sfx_peak = make_sfx(scenes_path, dur, sfx_wav)
    vol = 10 ** ((max_db(audio) - float(os.environ.get("SFX_DB", "12")) - sfx_peak) / 20)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", video_in, "-i", audio, "-i", sfx_wav, "-filter_complex", mix_graph(vol),
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", abr, "-ar", "48000", "-shortest",
                    "-movflags", "+faststart", out_mp4], check=True)
    print(out_mp4, os.path.getsize(out_mp4) // 1024 // 1024, "MB")


def max_db(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    for ln in out.splitlines():
        if "max_volume" in ln:
            return float(ln.split("max_volume:")[1].split("dB")[0])
    return -3.0


def make_grain():
    rng = np.random.default_rng(1)
    n = rng.normal(0, 1, (H, W)).astype(np.float32)
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = np.clip(np.abs(n) * 6, 0, 18).astype(np.uint8)
    return cairo.ImageSurface.create_for_data(memoryview(arr), cairo.FORMAT_ARGB32, W, H), arr


_GRAIN = None


def draw_scene(c, fn, t, start, end):
    c.save()
    k = 1 + 0.025 * clamp01((t - start) / max(1, end - start))  # zoom lento
    c.translate(W / 2, H / 2); c.scale(k, k); c.translate(-W / 2, -H / 2)
    fn(c, t)
    c.restore()


def render_frame(c, t, SCENES):
    global _GRAIN
    if _GRAIN is None:
        _GRAIN = make_grain()
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    background(c, t)
    idx = max(i for i, s in enumerate(SCENES) if s[0] <= t)
    st, en, fn = SCENES[idx]
    if idx > 0 and t < st + XF:
        pst, pen, pfn = SCENES[idx - 1]
        draw_scene(c, pfn, t, pst, pen)
        c.push_group(); background(c, t)
        draw_scene(c, fn, t, st, en)
        c.pop_group_to_source(); c.paint_with_alpha(ease_io((t - st) / XF))
    else:
        draw_scene(c, fn, t, st, en)
    overlay(c, t)
    c.set_source_surface(_GRAIN[0], 0, 0); c.paint_with_alpha(0.6)


def stills(scenes_path, out, times):
    S = load_scenes(scenes_path)
    os.makedirs(out, exist_ok=True)
    paths = []
    for t in times:
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
        render_frame(c, t, S)
        p = f"{out}/f_{t:07.2f}.png"; surf.write_to_png(p); paths.append(p)
    return paths


def sheet(scenes_path, out_png, times):
    tmp = tempfile.mkdtemp()
    stills(scenes_path, tmp, times)
    rows = (len(times) + 1) // 2
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-pattern_type", "glob", "-i", f"{tmp}/f_*.png",
                    "-vf", f"scale=960:-1,tile=2x{rows}", "-frames:v", "1", out_png], check=True)


def _segment(args):
    scenes_path, t0, t1, path = args
    S = load_scenes(scenes_path)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(surf)
    for f in range(round(t0 * FPS), round(t1 * FPS)):
        render_frame(c, f / FPS, S)
        surf.flush(); p.stdin.write(surf.get_data())
    p.stdin.close(); p.wait()
    return path


def build(scenes_path, audio, out_mp4, crf=26):
    """audio pode ser 'silent:<segundos>' para gerar prévia sem som"""
    silent = audio.startswith("silent:")
    if silent:
        dur = float(audio.split(":")[1])
    else:
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                             "-of", "csv=p=0", audio]).decode().strip())
    n = max(1, os.cpu_count() or 1)
    tmp = tempfile.mkdtemp()
    cuts = [dur * i / n for i in range(n + 1)]
    cuts = [round(x * FPS) / FPS for x in cuts]
    jobs = [(scenes_path, cuts[i], cuts[i + 1], f"{tmp}/seg{i:02d}.mp4") for i in range(n)]
    with ProcessPoolExecutor(n) as ex:
        segs = list(ex.map(_segment, jobs))
    with open(f"{tmp}/list.txt", "w") as f:
        for s in segs:
            f.write(f"file '{s}'\n")
    # concat + áudio + compressão final (fica ~20 MB para 4 min)
    ain = ["-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=44100:cl=stereo"] if silent else ["-i", audio]
    sfx_wav = f"{tmp}/sfx.wav"
    ncues, sfx_peak = make_sfx(scenes_path, dur, sfx_wav)
    # efeitos ficam SFX_DB abaixo do pico da narração (padrão 12 dB) para nunca competir com a voz
    narr_peak = -3.0 if silent else max_db(audio)
    sfx_db = float(os.environ.get("SFX_DB", "12"))
    vol = 10 ** ((narr_peak - sfx_db - sfx_peak) / 20)
    print(f"efeitos sonoros: {ncues} eventos, volume {vol:.2f}")
    mix = mix_graph(vol)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt",
                    *ain, "-i", sfx_wav, "-filter_complex", mix, "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", str(crf),
                    "-tune", "animation", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest",
                    "-movflags", "+faststart", out_mp4], check=True)
    print(out_mp4, os.path.getsize(out_mp4) // 1024 // 1024, "MB")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "stills":
        stills(sys.argv[2], sys.argv[3], [float(x) for x in sys.argv[4:]])
    elif cmd == "sheet":
        sheet(sys.argv[2], sys.argv[3], [float(x) for x in sys.argv[4:]])
    elif cmd == "build":
        build(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "remix":
        remix(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        print(__doc__)
