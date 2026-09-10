#!/usr/bin/env python3
"""Write checkerboard, black, white and alpha-bbox visual QA without trimming."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw


def generate(path, output):
    path, output = Path(path), Path(output)
    im = Image.open(path).convert('RGBA')
    results = []
    for kind in ('checkerboard', 'black', 'white', 'bbox'):
        bg = Image.new('RGBA', im.size, 'black' if kind == 'black' else 'white')
        if kind in ('checkerboard', 'bbox'):
            d = ImageDraw.Draw(bg)
            for y in range(0, im.height, 12):
                for x in range(0, im.width, 12):
                    if (x//12+y//12) % 2 == 0:
                        d.rectangle((x,y,x+11,y+11), fill=(185,185,185,255))
        bg = Image.alpha_composite(bg, im)
        box = im.getchannel('A').getbbox()
        if kind == 'bbox' and box:
            ImageDraw.Draw(bg).rectangle((box[0],box[1],box[2]-1,box[3]-1), outline='red', width=1)
        target = output/kind/(path.stem+'_'+kind+'.png')
        target.parent.mkdir(parents=True, exist_ok=True)
        bg.convert('RGB').save(target)
        results.append(str(target))
    return results


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('paths', nargs='+'); p.add_argument('--output', default='qa')
    a = p.parse_args()
    for path in a.paths:
        print('\n'.join(generate(path, a.output)))
