#!/usr/bin/env python3
"""Compare Unity capture to reference; derived from Donyzh's MIT image comparator."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageChops


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('expected'); p.add_argument('actual')
    p.add_argument('--threshold', type=int, default=8)
    p.add_argument('--max-changed-ratio', type=float, default=.01)
    p.add_argument('--diff'); p.add_argument('--json', action='store_true')
    a = p.parse_args()
    if not 0 <= a.threshold <= 255 or not 0 <= a.max_changed_ratio <= 1:
        p.error('Invalid comparison thresholds')
    expected = Image.open(a.expected).convert('RGBA'); actual = Image.open(a.actual).convert('RGBA')
    if expected.size != actual.size:
        print(json.dumps({'same_size': False, 'expected': expected.size, 'actual': actual.size})); return 1
    # Compare composites on both extremes and alpha; ignore RGB under alpha=0.
    arrays = []
    for color in ('black','white'):
        bg = Image.new('RGBA', expected.size, color)
        arrays.append(np.abs(np.asarray(Image.alpha_composite(bg,expected),dtype=float)-np.asarray(Image.alpha_composite(bg,actual),dtype=float)))
    delta = np.maximum(*arrays)
    alpha = np.abs(np.asarray(expected.getchannel('A'),dtype=float)-np.asarray(actual.getchannel('A'),dtype=float))
    changed = np.maximum(delta[...,:3].max(axis=2), alpha) > a.threshold
    result = {'same_size': True, 'changed_pixel_ratio': float(changed.mean()), 'mae': float(delta.mean()), 'alpha_mae': float(alpha.mean())}
    if a.diff:
        Path(a.diff).parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(np.uint8(delta[...,:3])).save(a.diff)
    print(json.dumps(result, indent=2))
    return int(result['changed_pixel_ratio'] > a.max_changed_ratio)


if __name__ == '__main__':
    raise SystemExit(main())
