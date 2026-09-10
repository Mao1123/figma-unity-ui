#!/usr/bin/env python3
"""Unity alpha audit. Adapted conceptually from Donyzh (MIT); strict per-asset policy."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from generate_alpha_preview import generate


def audit(path, policy=None):
    policy = policy or {}
    path = Path(path)
    with Image.open(path) as original:
        mode = original.mode
        has_alpha = mode in ('RGBA','LA') or 'transparency' in original.info
        im = original.convert('RGBA')
    arr = np.asarray(im)
    rgb, alpha = arr[..., :3].astype(float), arr[..., 3]
    visible = alpha > 0
    corners = [int(alpha[y,x]) for y,x in ((0,0),(0,-1),(-1,0),(-1,-1))]
    edges = {'left': alpha[:,0], 'right': alpha[:,-1], 'top': alpha[0,:], 'bottom': alpha[-1,:]}
    required = policy.get('alphaRequired', True)
    exception = policy.get('alphaPolicy', {})
    allowed_corners = exception.get('allowCornerAlpha', False)
    allowed_edges = exception.get('allowedTouchingEdges', [])
    # Compare semi-transparent colors with the opaque core. Flags are hypotheses,
    # not proof: legitimate white strokes or black shadows can trigger them.
    semi = (alpha > 4) & (alpha < 251)
    core = rgb[alpha >= 251]
    fringe = []
    if semi.any() and core.size:
        med = np.median(core, axis=0)
        candidates = {'white': (255,255,255), 'black': (0,0,0),
                      'blue': (0,0,255), 'purple': (128,0,128)}
        bg = policy.get('backgroundColor')
        if bg:
            candidates['background_contamination'] = tuple(int(bg.lstrip('#')[i:i+2],16) for i in (0,2,4))
        pixels = rgb[semi]
        for name, color in candidates.items():
            target = np.array(color)
            near = np.linalg.norm(pixels-target, axis=1) < 90
            if np.linalg.norm(med-target) > 110 and near.mean() > .08:
                fringe.append(name)
    rectangle = bool(visible.all() or (all(c > 250 for c in corners) and (alpha > 250).mean() > .95))
    transparent_ok = bool(has_alpha and (alpha == 0).any() and
                          (allowed_corners or max(corners) == 0) and not rectangle)
    errors = []
    if mode != 'RGBA': errors.append('PNG must be saved in RGBA mode')
    if not visible.any(): errors.append('Empty asset')
    if required and not transparent_ok: errors.append('Transparent background failed')
    for side, values in edges.items():
        if required and values.any() and side not in allowed_edges:
            errors.append('Possible clipping: '+side)
    if (allowed_corners or allowed_edges) and not exception.get('reason', '').strip():
        errors.append('Alpha exceptions require a design reason')
    bounds = policy.get('sourceBounds')
    size_ok = True
    if bounds:
        size_ok = im.size == (round(bounds['width']*policy['scaleFactor']), round(bounds['height']*policy['scaleFactor']))
        if not size_ok: errors.append('Pixel dimensions disagree with manifest')
    return {'path': str(path), 'width': im.width, 'height': im.height,
            'file_size': path.stat().st_size, 'mode': mode, 'rgba_mode': mode == 'RGBA',
            'has_alpha_channel': has_alpha, 'alphaRequired': required,
            'transparent_bg_ok': transparent_ok if required else True,
            'corner_alpha': corners, 'edge_alpha': {k: {'max': int(v.max()), 'mean': float(v.mean())} for k,v in edges.items()},
            'nontransparent_bbox': im.getchannel('A').getbbox(),
            **{'touching_'+k+'_edge': bool(v.any()) for k,v in edges.items()},
            'possible_background_rectangle': rectangle, 'possible_color_fringe': bool(fringe),
            'fringe_candidates': fringe, 'size_ok': size_ok, 'errors': errors,
            'status': 'FAIL' if errors else ('REVIEW' if fringe else 'PASS'),
            'visual_review_required': required}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('paths', nargs='*')
    p.add_argument('--manifest'); p.add_argument('--project-root', default='.')
    p.add_argument('--require-transparent-bg', action='store_true')
    p.add_argument('--allow-opaque', action='store_true')
    p.add_argument('--qa-dir', default='qa'); p.add_argument('--report')
    a = p.parse_args()
    jobs = []
    try:
        if a.require_transparent_bg and a.allow_opaque:
            raise ValueError('Conflicting transparency flags')
        if a.manifest:
            from validate_manifest import validate
            data = json.loads(Path(a.manifest).read_text(encoding='utf-8'))
            validate(data)
            for item in data['assets']:
                if item['format'] == 'png':
                    policy = dict(item)
                    if a.require_transparent_bg: policy['alphaRequired'] = True
                    jobs.append((Path(a.project_root)/item['unityPath'], policy))
        else:
            for raw in a.paths:
                f = Path(raw)
                paths = sorted(f.rglob('*.png')) if f.is_dir() else [f]
                jobs.extend((v, {'alphaRequired': not a.allow_opaque}) for v in paths)
        if not jobs: raise ValueError('No PNG assets found')
        results = []
        for index,(path,policy) in enumerate(jobs):
            result = audit(path, policy)
            # Keep separate asset folders so same basenames cannot overwrite QA.
            result['previews'] = generate(path, Path(a.qa_dir)/f'{index:03d}_{path.stem}')
            results.append(result)
        payload = json.dumps(results, indent=2)
        if a.report:
            Path(a.report).parent.mkdir(parents=True, exist_ok=True)
            Path(a.report).write_text(payload, encoding='utf-8')
        print(payload)
        return 1 if any(r['errors'] for r in results) else 0
    except (OSError, ValueError, KeyError) as e:
        p.exit(2, str(e)+'\n')


if __name__ == '__main__':
    raise SystemExit(main())
