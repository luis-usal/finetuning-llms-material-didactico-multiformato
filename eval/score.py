#!/usr/bin/env python3
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "eval"))
import metrics as M

CAMPOS = [
    "condicion", "perfil_id", "formato", "tema", "nivel", "lenguaje",
    "len_palabras", "fh", "inflesz", "rouge_l",
    "mcq_n", "mcq_bien_frac", "code_ok", "code_msg",
    "gold_fh", "gold_inflesz",
]


def fila_para(condicion, item):
    meta = item["meta"]
    gen = item["generado"] or ""
    gold = item["gold"] or ""
    formato = meta["formato"]
    f = {c: "" for c in CAMPOS}
    f.update({
        "condicion": condicion,
        "perfil_id": meta["perfil_id"],
        "formato": formato,
        "tema": meta["tema"],
        "nivel": meta["nivel"],
        "lenguaje": meta["lenguaje"],
        "len_palabras": M.n_palabras(gen),
        "fh": M.fernandez_huerta(gen),
        "inflesz": M.inflesz(gen),
        "gold_fh": M.fernandez_huerta(gold),
        "gold_inflesz": M.inflesz(gold),
    })
    if formato in ("explicacion", "ficha"):
        f["rouge_l"] = M.rouge_l(gold, gen)
    elif formato == "mcq":
        n, bien = M.mcq_bien_formada(gen)
        f["mcq_n"] = n
        f["mcq_bien_frac"] = round(bien / n, 3) if n else 0.0
    elif formato == "ejercicio_resuelto":
        codigo = M.extraer_codigo(gen)
        if meta["lenguaje"] == "python":
            ok, msg = M.ejecuta_python(codigo)
            f["code_ok"] = int(ok)
            f["code_msg"] = msg
        else:
            f["code_ok"] = ""
            f["code_msg"] = "no-python"
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condicion", required=True)
    ap.add_argument("--gen", default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    gen_path = Path(args.gen) if args.gen else ROOT / "eval" / "results" / f"gen_{args.condicion}.jsonl"
    out_path = Path(args.out) if args.out else ROOT / "eval" / "results" / f"metrics_{args.condicion}.csv"

    items = [json.loads(l) for l in gen_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    filas = [fila_para(args.condicion, it) for it in items]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(filas)

    print(f"{len(filas)} filas -> {out_path}")


if __name__ == "__main__":
    main()
