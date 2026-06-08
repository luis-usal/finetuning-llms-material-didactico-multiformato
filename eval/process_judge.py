#!/usr/bin/env python3
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"

CRITERIOS = [
    "crit_correccion_tecnica", "crit_adecuacion_nivel", "crit_alineacion_objetivos",
    "crit_atencion_errores", "crit_claridad_estructura", "crit_cumplimiento_formato",
    "crit_estilo",
]


def cargar_veredictos(path):
    txt = Path(path).read_text(encoding="utf-8")
    m = re.search(r'\[\s*\{\s*"jid"', txt)
    if not m:
        raise SystemExit("No se encontro el array de veredictos del juez")
    obj, _ = json.JSONDecoder().raw_decode(txt[m.start():])
    return obj


def main():
    salida = sys.argv[1]
    veredictos = cargar_veredictos(salida)
    mapa = json.loads((RES / "judge_map.json").read_text(encoding="utf-8"))

    filas = {"prompting": [], "finetuned": []}
    for v in veredictos:
        jid = v["jid"]
        info = mapa[jid]
        media = sum(v[c] for c in CRITERIOS) / len(CRITERIOS)
        fila = {
            "jid": jid,
            "condicion": info["condicion"],
            "formato": info["formato"],
            "nivel": info["nivel"],
            **{c: v[c] for c in CRITERIOS},
            "media": round(media, 3),
        }
        filas[info["condicion"]].append(fila)

    campos = ["jid", "condicion", "formato", "nivel"] + CRITERIOS + ["media"]
    for cond, fs in filas.items():
        out = RES / f"judge_{cond}.csv"
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=campos)
            w.writeheader()
            w.writerows(fs)
        print(f"{cond}: {len(fs)} items -> {out}")

    print("\n=== Medias por criterio (1-4) ===")
    print(f"{'criterio':30} {'prompting':>10} {'finetuned':>10}")
    for c in CRITERIOS + ["media"]:
        def avg(cond):
            fs = filas[cond]
            vals = [x[c] for x in fs]
            return sum(vals) / len(vals) if vals else 0
        print(f"{c:30} {avg('prompting'):>10.2f} {avg('finetuned'):>10.2f}")

    print("\n=== Media global por formato ===")
    for fmt in ["explicacion", "ficha", "mcq", "ejercicio_resuelto"]:
        def avgf(cond):
            vals = [x["media"] for x in filas[cond] if x["formato"] == fmt]
            return sum(vals) / len(vals) if vals else 0
        print(f"  {fmt:20} prompting={avgf('prompting'):.2f}  finetuned={avgf('finetuned'):.2f}")


if __name__ == "__main__":
    main()
