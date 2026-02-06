#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pybryt


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--notebook", required=True, type=Path, help="Annotated reference notebook (.ipynb)")
    p.add_argument("--out", required=True, type=Path, help="Output .pkl path")
    p.add_argument("--display-name", default=None, help="Optional display name for reference")
    args = p.parse_args()

    refs = pybryt.ReferenceImplementation.compile(str(args.notebook), display_name=args.display_name)
    if not isinstance(refs, list):
        refs = [refs]

    if len(refs) == 1:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        refs[0].dump(str(args.out))
        print(f"Saved reference to {args.out}")
        return

    stem = args.out.stem
    for i, r in enumerate(refs, start=1):
        out_i = args.out.with_name(f"{stem}_{i}.pkl")
        out_i.parent.mkdir(parents=True, exist_ok=True)
        r.dump(str(out_i))
        print(f"Saved reference {i} to {out_i}")


if __name__ == "__main__":
    main()
