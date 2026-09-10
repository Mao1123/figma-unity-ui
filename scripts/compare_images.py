#!/usr/bin/env python3
"""Compare Unity capture to reference; derived from Donyzh's MIT image comparator."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image


def metrics(delta, threshold, limit):
    changed = delta.max(axis=2) > threshold
    ratio = float(changed.mean())
    return {'changed_pixel_ratio': ratio, 'mae': float(delta.mean()),
            'alpha_mae': float(delta[..., 3].mean()),
            'max_delta': int(delta.max()), 'numerical_pass': ratio <= limit}


def compare(expected, actual, threshold=0, limit=0, regions=None):
    if expected.size != actual.size:
        return {'same_size': False, 'numerical_pass': False,
                'expected': expected.size, 'actual': actual.size}, None
    expected = expected.convert('RGBA'); actual = actual.convert('RGBA')
    arrays = []
    for color in ('black', 'white'):
        bg = Image.new('RGBA', expected.size, color)
        arrays.append(np.abs(np.asarray(Image.alpha_composite(bg, expected), dtype=float)
                             - np.asarray(Image.alpha_composite(bg, actual), dtype=float)))
    delta = np.maximum(*arrays)
    delta[..., 3] = np.abs(np.asarray(expected.getchannel('A'), dtype=float)
                          - np.asarray(actual.getchannel('A'), dtype=float))
    result = {'same_size': True, **metrics(delta, threshold, limit), 'regions': []}
    names = set()
    if not isinstance(regions or [], list):
        raise ValueError('Regions must be a JSON array')
    for region in regions or []:
        name = region['name']
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError('Region names must be nonempty and unique')
        names.add(name)
        x,y,w,h = (region[k] for k in ('x','y','width','height'))
        if any(type(v) is not int for v in (x,y,w,h)) or min(x,y)<0 or min(w,h)<1 or x+w>expected.width or y+h>expected.height:
            raise ValueError('Region outside reference or invalid integer bounds: '+name)
        record = {'name': name, 'bounds': [x,y,w,h],
                  **metrics(delta[y:y+h,x:x+w], threshold, limit)}
        result['regions'].append(record)
        result['numerical_pass'] &= record['numerical_pass']
    return result, delta


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('expected'); p.add_argument('actual')
    p.add_argument('--threshold', type=int, default=0)
    p.add_argument('--max-changed-ratio', type=float, default=0)
    p.add_argument('--exact', action='store_true', help='Require zero visible pixel differences')
    p.add_argument('--measure-only', action='store_true', help='Diagnostic metrics only; never an acceptance PASS')
    p.add_argument('--regions', help='JSON array of named reference-pixel bounds')
    p.add_argument('--overlay'); p.add_argument('--report')
    p.add_argument('--diff'); p.add_argument('--json', action='store_true')
    a = p.parse_args()
    if not 0 <= a.threshold < 255 or not 0 <= a.max_changed_ratio < 1:
        p.error('Vacuous thresholds are forbidden: threshold < 255 and ratio < 1 required')
    if a.exact and (a.threshold or a.max_changed_ratio):
        p.error('--exact conflicts with nonzero tolerances')
    try:
        regions = json.loads(Path(a.regions).read_text(encoding='utf-8')) if a.regions else []
        expected = Image.open(a.expected).convert('RGBA'); actual = Image.open(a.actual).convert('RGBA')
        result, delta = compare(expected, actual, a.threshold, a.max_changed_ratio, regions)
        result.update(threshold=a.threshold, max_changed_ratio=a.max_changed_ratio,
                      visual_review_required=True, mode='measure_only' if a.measure_only else 'acceptance')
        result['status'] = 'MEASURED' if a.measure_only else ('NUMERICAL_PASS' if result['numerical_pass'] else 'FAIL')
        if a.measure_only: result['numerical_pass'] = None
        if delta is not None:
            if a.diff:
                target = Path(a.diff); target.parent.mkdir(parents=True, exist_ok=True)
                Image.fromarray(np.uint8(delta[..., :3])).save(target)
            if a.overlay:
                target = Path(a.overlay); target.parent.mkdir(parents=True, exist_ok=True)
                Image.blend(expected, actual, .5).save(target)
            if a.report:
                crops = Path(a.report).parent/'regions'; crops.mkdir(parents=True, exist_ok=True)
                for index, record in enumerate(result['regions']):
                    x,y,w,h = record['bounds']; box=(x,y,x+w,y+h)
                    for label, im in (('reference',expected),('actual',actual)):
                        im.crop(box).save(crops/f'{index:03d}_{label}.png')
        payload = json.dumps(result, indent=2)
        if a.report:
            Path(a.report).parent.mkdir(parents=True, exist_ok=True)
            Path(a.report).write_text(payload, encoding='utf-8')
        print(payload)
        return 0 if a.measure_only else int(not result['numerical_pass'])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(2, str(exc)+'\n')


if __name__ == '__main__':
    raise SystemExit(main())
