#!/usr/bin/env python3
"""Re-pull a frame from Figma: print its layer tree, refresh its reference render.

    export FIGMA_TOKEN=…
    python3 tools/refresh.py 445:460            # tree + reference render
    python3 tools/refresh.py 445:460 --plate 445:463   # also re-export a background plate

The tree is what you diff against the HTML by hand: every line carries the position,
size, font and colour the poster should be using.
"""
import argparse
import json
import os
import pathlib
import sys
import urllib.request

FILE_KEY = "NvQSCDtYClyN1TLhZ2UK6l"
ROOT = pathlib.Path(__file__).resolve().parent.parent

FRAMES = {
    "445:377": "01-roadmap-696x1237",
    "445:394": "02-levels-1200x675",
    "445:438": "03-signup-675x1200",
    "445:451": "04-poster-1024x1401",
    "445:460": "05-rules-1200x675",
}
PLATES = {
    "445:379": "01-roadmap-bg",
    "445:395": "02-levels-bg",
    "445:439": "03-signup-bg",
    "445:453": "04-poster-bg",
    "445:463": "05-rules-bg",
}


def api(path):
    token = os.environ.get("FIGMA_TOKEN")
    if not token:
        sys.exit("FIGMA_TOKEN is not set.")
    req = urllib.request.Request(
        "https://api.figma.com/v1/" + path, headers={"X-Figma-Token": token}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def hex_of(color):
    return "#%02X%02X%02X" % tuple(round(color[k] * 255) for k in "rgb")


def describe(node, ox, oy, depth, visible, out):
    shown = node.get("visible", True) and visible
    if shown:
        box = node.get("absoluteBoundingBox") or {}
        line = f'{"  " * depth}{node["type"][:6]:<6} {node.get("name", "")[:32]:<32}'
        if box:
            line += (
                f' ({box.get("x", 0) - ox:.0f},{box.get("y", 0) - oy:.0f})'
                f' {box.get("width", 0):.0f}x{box.get("height", 0):.0f}'
            )
        if node["type"] == "TEXT":
            st = node.get("style", {})
            line += (
                f'  {st.get("fontFamily")} {st.get("fontWeight")} {st.get("fontSize")}'
                f'/{st.get("lineHeightPx", 0):.1f} ls={st.get("letterSpacing", 0)}'
                f' {st.get("textAlignHorizontal")}/{st.get("textAlignVertical")}'
                f'  {json.dumps(node.get("characters", "")[:60], ensure_ascii=False)}'
            )
        for fill in node.get("fills") or []:
            if fill.get("visible") is not False and fill["type"] == "SOLID":
                line += f'  fill={hex_of(fill["color"])}'
        for fx in node.get("effects") or []:
            if fx.get("visible", True):
                line += f'  fx={fx["type"]}({fx.get("radius", "")})'
        out.append(line)
    for child in node.get("children", []):
        describe(child, ox, oy, depth + 1, shown, out)


def download(url, path):
    with urllib.request.urlopen(url) as r, open(path, "wb") as f:
        while chunk := r.read(1 << 16):
            f.write(chunk)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nodes", nargs="+", help="frame ids, e.g. 445:460")
    ap.add_argument("--plate", action="append", default=[], help="background node id to re-export at 2x")
    args = ap.parse_args()

    data = api(f"files/{FILE_KEY}/nodes?ids={','.join(args.nodes)}")
    print(f'{data.get("name")} · last modified {data.get("lastModified")}\n')
    for nid in args.nodes:
        entry = data["nodes"].get(nid)
        if not entry:
            print(f"{nid}: not found"); continue
        doc = entry["document"]
        box = doc["absoluteBoundingBox"]
        out = []
        describe(doc, box["x"], box["y"], 0, True, out)
        print("=" * 100)
        print(nid, "—", doc["name"])
        print("\n".join(out), "\n")

    wanted = {n: FRAMES[n] for n in args.nodes if n in FRAMES}
    if wanted:
        imgs = api(f'images/{FILE_KEY}?ids={",".join(wanted)}&format=png&scale=1')["images"]
        for nid, name in wanted.items():
            path = ROOT / "reference" / f"{name}.png"
            download(imgs[nid], path)
            print(f"reference/{path.name} refreshed  (convert to .webp before committing)")

    if args.plate:
        imgs = api(f'images/{FILE_KEY}?ids={",".join(args.plate)}&format=png&scale=2')["images"]
        for nid in args.plate:
            name = PLATES.get(nid, nid.replace(":", "-"))
            path = ROOT / "assets" / "img" / f"{name}.png"
            download(imgs[nid], path)
            print(f"assets/img/{path.name} refreshed  (convert to .webp before committing)")


if __name__ == "__main__":
    main()
