#!/usr/bin/env python3
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "eval" / "results"
ITEMS = RES / "judge_items"
ITEMS.mkdir(parents=True, exist_ok=True)

tareas = []
for cond in ["prompting", "finetuned"]:
    fp = RES / f"gen_{cond}.jsonl"
    for it in (json.loads(l) for l in fp.read_text(encoding="utf-8").splitlines() if l.strip()):
        tareas.append({
            "condicion": cond,
            "meta": it["meta"],
            "perfil": it["system"],
            "user": it["user"],
            "generado": it["generado"],
        })

random.Random(0).shuffle(tareas)

mapa = {}
for i, t in enumerate(tareas):
    jid = f"J{i:03d}"
    (ITEMS / f"{jid}.json").write_text(json.dumps({
        "perfil": t["perfil"],
        "user": t["user"],
        "generado": t["generado"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    mapa[jid] = {"condicion": t["condicion"], **t["meta"]}

(RES / "judge_map.json").write_text(json.dumps(mapa, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"{len(tareas)} items -> {ITEMS}/  (mapa en judge_map.json)")
print("jids:", " ".join(sorted(mapa.keys())))
