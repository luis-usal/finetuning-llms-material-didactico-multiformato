#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--condicion", required=True, choices=["prompting", "finetuned"])
    ap.add_argument("--modelo", default="mlx-community/Qwen3-4B-Instruct-2507-4bit")
    ap.add_argument("--adapter", default=str(ROOT / "train" / "adapters"),
                    help="ruta del adapter QLoRA, solo se usa en condicion finetuned")
    ap.add_argument("--test", default=str(ROOT / "data" / "test_annotado.jsonl"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-tokens", type=int, default=900)
    ap.add_argument("--temp", type=float, default=0.0)
    ap.add_argument("--limit", type=int, default=0, help="si >0, genera solo los primeros N items (pruebas)")
    args = ap.parse_args()

    from mlx_lm import load, generate
    try:
        from mlx_lm.sample_utils import make_sampler
        sampler = make_sampler(temp=args.temp)
    except Exception:
        sampler = None

    adapter = args.adapter if args.condicion == "finetuned" else None
    print(f"Cargando modelo {args.modelo}" + (f" + adapter {adapter}" if adapter else " (sin adapter)"))
    model, tokenizer = load(args.modelo, adapter_path=adapter)

    items = [json.loads(l) for l in Path(args.test).read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.limit:
        items = items[: args.limit]

    out_path = Path(args.out) if args.out else ROOT / "eval" / "results" / f"gen_{args.condicion}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        for i, item in enumerate(items, 1):
            msgs = item["messages"]
            system = msgs[0]["content"]
            user = msgs[1]["content"]
            gold = msgs[2]["content"]
            prompt = tokenizer.apply_chat_template(
                [{"role": "system", "content": system}, {"role": "user", "content": user}],
                add_generation_prompt=True,
                tokenize=False,
            )
            kwargs = dict(max_tokens=args.max_tokens, verbose=False)
            if sampler is not None:
                kwargs["sampler"] = sampler
            generado = generate(model, tokenizer, prompt=prompt, **kwargs)
            f.write(json.dumps({
                "meta": item["meta"],
                "system": system,
                "user": user,
                "gold": gold,
                "generado": generado,
            }, ensure_ascii=False) + "\n")
            if i % 10 == 0 or i == len(items):
                print(f"  {i}/{len(items)}")

    print(f"-> {out_path}")


if __name__ == "__main__":
    main()
