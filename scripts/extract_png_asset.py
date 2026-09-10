#!/usr/bin/env python3
"""Fixed-canvas extraction, adapted from Donyzh's MIT image-to-code workflow.

An explicit grayscale matte is needed to recover soft edges from a flattened
known-background image. Color keying alone cannot recover arbitrary shadows.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image


def extract(source, output, x, y, width, height, scale_factor=2,
            source_scale=1, mask=None, background=None):
    if scale_factor not in (1, 2, 3, 4) or source_scale <= 0:
        raise ValueError('Export scale must be 1/2/3/4; source scale must be positive')
    if min(x, y) < 0 or min(width, height) <= 0:
        raise ValueError('Invalid bbox')
    image = Image.open(source).convert('RGBA')
    coords = [v * source_scale for v in (x, y, x + width, y + height)]
    box = tuple(round(v) for v in coords)
    if box[2] > image.width or box[3] > image.height or box[2] <= box[0] or box[3] <= box[1]:
        raise ValueError('BBox exceeds source or rounds to empty pixels')
    crop = image.crop(box)
    if background and mask is None:
        raise ValueError('Background unmatting requires an explicit grayscale mask')
    if mask:
        matte = Image.open(mask)
        if matte.mode != 'L' or matte.size != crop.size:
            raise ValueError('Mask must be L mode at the unscaled crop pixel size')
        a = np.asarray(matte, dtype=np.float32) / 255.0
        rgb = np.asarray(crop, dtype=np.float32)[..., :3]
        if background:
            value = background.lstrip('#')
            if len(value) != 6:
                raise ValueError('Background must be #RRGGBB')
            bg = np.array([int(value[i:i+2], 16) for i in (0, 2, 4)])
            rgb = (rgb - (1-a[..., None])*bg) / np.maximum(a[..., None], 1/255)
        pixels = np.zeros((*a.shape, 4), dtype=np.uint8)
        pixels[..., :3] = np.rint(np.clip(rgb, 0, 255)).astype(np.uint8)
        pixels[..., 3] = np.rint(a*255).astype(np.uint8)
        pixels[a == 0, :3] = 0
        crop = Image.fromarray(pixels, 'RGBA')
    size = (round(width*scale_factor), round(height*scale_factor))
    if min(size) < 1:
        raise ValueError('Output rounds to empty pixels')
    # Premultiplied resampling prevents invisible RGB from bleeding into edges.
    crop = crop.convert('RGBa').resize(size, Image.Resampling.LANCZOS).convert('RGBA')
    output = Path(output)
    if output.suffix.lower() != '.png':
        raise ValueError('Output must be PNG')
    output.parent.mkdir(parents=True, exist_ok=True)
    crop.save(output)
    return {'sourceBounds': dict(zip(('x','y','width','height'), (x,y,width,height))),
            'scaleFactor': scale_factor, 'pixelWidth': size[0], 'pixelHeight': size[1],
            'resampledBeyondSource': scale_factor > source_scale}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source'); p.add_argument('output')
    for key in ('x', 'y', 'width', 'height'):
        p.add_argument('--'+key, type=float, required=True)
    p.add_argument('--scale-factor', type=int, choices=(1,2,3,4), default=2)
    p.add_argument('--source-scale', type=float, default=1,
                   help='Source pixels per design unit; bbox is in design units')
    p.add_argument('--mask', help='L-mode alpha matte matching source crop pixels')
    p.add_argument('--background', help='Known flattened background #RRGGBB; requires mask')
    args = vars(p.parse_args())
    try:
        print(json.dumps(extract(**args), indent=2))
        return 0
    except (ValueError, OSError) as e:
        p.exit(2, str(e)+'\n')


if __name__ == '__main__':
    raise SystemExit(main())
