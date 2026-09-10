#!/usr/bin/env python3
"""Generate original geometric demo art, manifests and standard Unity directories."""
import argparse
import shutil
from pathlib import Path
from PIL import Image, ImageDraw


def create(root):
    root = Path(root)
    for directory in ('Backgrounds','Panels','Buttons','Icons','Cards','Decorations','Illustrations','Source',
                      'Prefabs/Common','Prefabs/Buttons','Prefabs/Panels','Prefabs/Screens',
                      'Scripts/Runtime','Scripts/Editor','FigmaSync'):
        (root/'Assets/UI'/directory).mkdir(parents=True, exist_ok=True)
    icon = Image.new('RGBA',(96,96))
    ImageDraw.Draw(icon).line([(60,21),(33,48),(60,75)],fill='#123b46',width=9,joint='curve')
    panel = Image.new('RGBA',(192,192))
    ImageDraw.Draw(panel).rounded_rectangle((4,4,187,187),radius=32,fill='#ffffff')
    targets=[root/'Assets/UI/Icons/icon_back.png',root/'Assets/UI/Panels/panel_information.png']
    source=Path(__file__).resolve().parents[1]
    copies=[(source/'examples'/f'figma_{kind}_manifest.example.json', root/'Assets/UI/FigmaSync'/f'figma_{kind}_manifest.json') for kind in ('asset','ui')]
    copies += [(f,root/'Assets/UI/Scripts/Editor'/f.name) for f in (source/'unity/Editor').glob('*.cs')]
    if any(p.exists() for p in targets+[b for _,b in copies]):
        raise ValueError('Example output already exists; choose a new example directory')
    icon.save(targets[0]); panel.save(targets[1])
    for a,b in copies: shutil.copyfile(a,b)
    return targets


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--project-root',required=True)
    a=p.parse_args(); print('\n'.join(str(p) for p in create(a.project_root)))
