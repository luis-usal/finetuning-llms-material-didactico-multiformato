#!/usr/bin/env python3
import re
import subprocess
import sys
import tempfile
from pathlib import Path

VOCALES = "aeiouáéíóúü"


def _palabras(texto):
    return re.findall(r"[a-záéíóúüñ]+", texto.lower())


def _silabas_palabra(palabra):

    grupos = re.findall(rf"[{VOCALES}]+", palabra)
    return max(1, len(grupos))


def _frases(texto):
    trozos = re.split(r"[.!?]+", texto)
    return [t for t in trozos if t.strip()]


def _conteos(texto):
    palabras = _palabras(texto)
    n_pal = len(palabras)
    n_sil = sum(_silabas_palabra(p) for p in palabras)
    n_fra = max(1, len(_frases(texto)))
    return n_pal, n_sil, n_fra


def fernandez_huerta(texto):
    n_pal, n_sil, n_fra = _conteos(texto)
    if n_pal == 0:
        return 0.0
    return round(206.84 - 60.0 * (n_sil / n_pal) - 102.0 * (n_fra / n_pal), 2)


def inflesz(texto):
    n_pal, n_sil, n_fra = _conteos(texto)
    if n_pal == 0:
        return 0.0
    return round(206.835 - 62.3 * (n_sil / n_pal) - (n_pal / n_fra), 2)


def _lcs(a, b):
    m, n = len(a), len(b)
    if m == 0 or n == 0:
        return 0
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]


def rouge_l(referencia, hipotesis):
    ref = _palabras(referencia)
    hyp = _palabras(hipotesis)
    if not ref or not hyp:
        return 0.0
    lcs = _lcs(ref, hyp)
    prec = lcs / len(hyp)
    rec = lcs / len(ref)
    if prec + rec == 0:
        return 0.0
    return round(2 * prec * rec / (prec + rec), 4)


def mcq_bien_formada(texto):

    bloques = re.split(r"(?i)respuesta\s+correcta\s*:\s*", texto)

    respuestas = re.findall(r"(?i)respuesta\s+correcta\s*:\s*([A-D])", texto)

    n_preguntas = len(respuestas)
    bien = 0

    opciones_a = len(re.findall(r"(?im)^\s*A[\).\-]", texto))


    partes = re.split(r"(?i)respuesta\s+correcta\s*:\s*[A-D]", texto)
    for parte in partes[:-1] if len(partes) > 1 else []:
        letras = set(re.findall(r"(?im)^\s*([A-D])[\).\-]", parte))
        if {"A", "B", "C", "D"}.issubset(letras):
            bien += 1
    if n_preguntas == 0:
        n_preguntas = max(opciones_a, 0)
    return n_preguntas, bien


def extraer_codigo(texto, lenguaje=None):
    m = re.search(r"```[a-zA-Z]*\n(.*?)```", texto, re.DOTALL)
    if m:
        return m.group(1).strip()
    return None


def ejecuta_python(codigo, timeout=10):
    if not codigo:
        return False, "sin codigo"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(codigo)
        ruta = f.name
    try:
        r = subprocess.run([sys.executable, ruta], capture_output=True, text=True, timeout=timeout)
        ok = r.returncode == 0
        msg = "ok" if ok else (r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "error")
        return ok, msg
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:
        return False, str(e)
    finally:
        Path(ruta).unlink(missing_ok=True)


def n_palabras(texto):
    return len(_palabras(texto))
