#!/usr/bin/env python3
"""Overlay Unity manifest sourceBounds; adapted from Donyzh (MIT)."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source'); p.add_argument('manifest'); p.add_argument('output')
    p.add_argument('--source-scale', type=float, default=1)
    a = p.parse_args()
    from validate_manifest import validate
    data = json.loads(Path(a.manifest).read_text(encoding='utf-8')); validate(data)
    if a.source_scale <= 0: p.error('source-scale must be positive')
    im = Image.open(a.source).convert('RGBA'); draw = ImageDraw.Draw(im)
    for item in data['assets']:
        b = item['sourceBounds']; x,y,w,h = [b[k]*a.source_scale for k in ('x','y','width','height')]
        if x < 0 or y < 0 or x+w > im.width or y+h > im.height:
            p.error('BBox outside source: '+item['nodeId'])
        draw.rectangle((x,y,x+w-1,y+h-1), outline='red', width=2)
        draw.text((x+2,y+2), item['fileName'], fill='red')
    Path(a.output).parent.mkdir(parents=True, exist_ok=True); im.save(a.output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
