"""Junta os blocos de narração em um único .wav, com 1,0 s de silêncio entre eles.

    python juntar_blocos.py saida.wav bloco1.mp3 bloco2.mp3 ...

IMPORTANTE: todas as entradas (inclusive o silêncio do anullsrc) são forçadas para float 44,1 kHz mono.
Sem isso o filtro concat do ffmpeg pode negociar áudio de 8 bits, o que cria um chiado que só aparece
quando o narrador fala (foi o ruído do MH370 e da 1ª versão do Mary Celeste).
No fim o script confere cada bloco contra o original e acusa se a diferença passar de -90 dB.
"""
import subprocess
import sys

import numpy as np

SR = 44100
FMT = f"aformat=sample_fmts=flt:sample_rates={SR}:channel_layouts=mono"


def decode(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)


def join(out, blocks, gap=1.0):
    args, chains, order = [], [], []
    for i, b in enumerate(blocks):
        args += ["-i", b]
        chains.append(f"[{i}:a]{FMT}[a{i}]")
    n = len(blocks)
    args += ["-f", "lavfi", "-t", str(gap), "-i", f"anullsrc=r={SR}:cl=mono"]
    if n > 1:
        chains.append(f"[{n}:a]{FMT},asplit={n - 1}" + "".join(f"[s{i}]" for i in range(n - 1)))
    for i in range(n):
        order.append(f"[a{i}]")
        if i < n - 1:
            order.append(f"[s{i}]")
    graph = ";".join(chains) + ";" + "".join(order) + f"concat=n={len(order)}:v=0:a=1"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", graph, "-c:a", "pcm_s16le", out], check=True)
    # conferência
    full = decode(out)
    pos = 0
    for b in blocks:
        src = decode(b)
        seg = full[pos:pos + len(src)]
        m = min(len(seg), len(src))
        diff = 20 * np.log10(np.sqrt(np.mean((seg[:m] - src[:m]) ** 2)) + 1e-12)
        flag = "ok" if diff < -90 else "ATENÇÃO: áudio alterado"
        print(f"{b}: {len(src) / SR:.3f}s, início {pos / SR:.3f}s, diferença {diff:.0f} dB -> {flag}")
        pos += len(src) + int(round(gap * SR))
    print(out, f"{len(full) / SR:.3f}s")


if __name__ == "__main__":
    join(sys.argv[1], sys.argv[2:])
