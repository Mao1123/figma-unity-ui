#!/usr/bin/env python3
"""Validate versioned manifests, safe Unity paths, references and pixel dimensions."""
import argparse
import json
import re
from pathlib import Path, PurePosixPath
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = {'bg':'Backgrounds','panel':'Panels','btn':'Buttons','icon':'Icons',
           'card':'Cards','deco':'Decorations','illustration':'Illustrations'}


def asset_name(name, fmt='png'):
    parts = name.split('/')
    if len(parts) != 3 or parts[0] != 'export' or parts[1] not in FOLDERS:
        raise ValueError('Expected export/<category>/<semantic_name>')
    if not re.fullmatch(r'[a-z]+(?:_[a-z]+)*', parts[2]) or 'copy' in parts[2].split('_'):
        raise ValueError('Use lowercase English semantic words; no copy/numeric suffixes')
    return parts[1]+'_'+parts[2]+'.'+fmt


def safe_path(value):
    parts = PurePosixPath(value).parts
    if '\\' in value or ':' in value or not parts or parts[0] != 'Assets' or any(p in ('.','..','') for p in value.split('/')):
        raise ValueError('Unsafe Unity path: '+value)


def validate(data, project_root=None, assets=None):
    kind = 'asset' if 'assets' in data else 'ui'
    schema = json.loads((ROOT/'references'/f'figma_{kind}_manifest.schema.json').read_text(encoding='utf-8'))
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: str(e.path))
    if errors:
        raise ValueError('; '.join(f'{list(e.path)}: {e.message}' for e in errors))
    if kind == 'asset':
        ids, paths = set(), set()
        for item in data['assets']:
            path = item['unityPath']; safe_path(path)
            if item['nodeId'] in ids or path.casefold() in paths:
                raise ValueError('Duplicate asset nodeId or path')
            ids.add(item['nodeId']); paths.add(path.casefold())
            if asset_name(item['figmaName'],item['format']) != item['fileName'] or PurePosixPath(path).name != item['fileName']:
                raise ValueError('Name mapping disagrees: '+path)
            if item['figmaName'].split('/')[1] != item['assetType']:
                raise ValueError('assetType disagrees with export category')
            b = item['sourceBounds']; s = item['scaleFactor']
            width,height = round(b['width']*s),round(b['height']*s)
            if min(width,height) < 1: raise ValueError('Empty pixel canvas')
            border = item.get('border', [0,0,0,0])
            if border[0]+border[2] >= b['width'] or border[1]+border[3] >= b['height']:
                raise ValueError('9-slice borders consume the center')
            if item['nineSlice'] and (not any(border) or item['format'] != 'png'):
                raise ValueError('9-slice requires PNG and nonzero border')
            if not item['nineSlice'] and any(border): raise ValueError('Border requires nineSlice')
            if not item['alphaRequired'] and not item.get('notes','').strip():
                raise ValueError('Opaque assets require a design reason in notes')
            policy = item.get('alphaPolicy',{})
            if (policy.get('allowCornerAlpha') or policy.get('allowedTouchingEdges')) and not policy.get('reason','').strip():
                raise ValueError('Alpha exception requires reason')
            if project_root:
                root = Path(project_root).resolve(); f = (root/path).resolve()
                if not f.is_relative_to(root): raise ValueError('Asset escapes project through symlink')
                if not f.is_file(): raise ValueError('Missing file: '+path)
                if item['format'] == 'png':
                    from PIL import Image
                    with Image.open(f) as im:
                        if im.size != (width,height): raise ValueError('Wrong pixel dimensions: '+path)
                        if im.mode != 'RGBA': raise ValueError('Expected RGBA: '+path)
    else:
        safe_path(data['unityPrefab'])
        if data.get('fontAsset'): safe_path(data['fontAsset'])
        nodes = data['nodes']; ids = {n['id'] for n in nodes}
        if len(ids) != len(nodes): raise ValueError('Duplicate hierarchy id')
        by_id = {n['id']:n for n in nodes}
        asset_ids = {a['nodeId'] for a in assets['assets']} if assets else None
        sibling_names = set()
        for n in nodes:
            key = (n['parentId'],n['name'])
            if key in sibling_names: raise ValueError('Duplicate sibling name')
            sibling_names.add(key)
            if n['parentId'] and n['parentId'] not in ids: raise ValueError('Missing parent')
            seen = {n['id']}; parent = n['parentId']
            while parent:
                if parent in seen: raise ValueError('Hierarchy cycle')
                seen.add(parent); parent = by_id[parent]['parentId']
            if n.get('assetNodeId') and asset_ids is not None and n['assetNodeId'] not in asset_ids:
                raise ValueError('Missing asset reference')
            if n['kind'] == 'Text' and not n.get('text'): raise ValueError('Text content required')
            if n.get('prefabPath'): safe_path(n['prefabPath'])
            if n['kind'] == 'Instance' and not n.get('prefabPath'): raise ValueError('Instance needs prefabPath')
    return kind


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest'); p.add_argument('--project-root'); p.add_argument('--assets')
    a = p.parse_args()
    try:
        data = json.loads(Path(a.manifest).read_text(encoding='utf-8'))
        assets = json.loads(Path(a.assets).read_text(encoding='utf-8')) if a.assets else None
        if assets: validate(assets, a.project_root)
        print('PASS '+validate(data,a.project_root,assets)+' manifest')
    except (ValueError, OSError, KeyError) as e:
        p.exit(1,str(e)+'\n')


if __name__ == '__main__':
    main()
