# Fixed bounds and clean assets

Measure `x/y/width/height` in design units relative to the Figma root's top-left.
Subtract the root absolute origin from Figma absolute bounds. For rotated nodes,
use a wrapper/export frame covering the axis-aligned rendered bounds; record the
rotation in design notes and reconstruct intentionally. Include effects in export
bounds, not just geometric bounds. Export a fixed wrapper if Figma tight export
bounds would discard padding. Screenshot pixel coordinates divide by sourceScale.

Classify before extraction:

| Content | Preferred result |
|---|---|
| Circle, rounded Button, Card, Tab, Badge, Progress, Divider, Input | Native Figma geometry; Unity Image/shared shape Sprite or project shape component |
| Simple icon | Original vector/SVG, then transparent PNG |
| Texture, illustration, artistic gradient, complex glow | Independent PNG/SVG with editable text removed |
| Text | TextMeshProUGUI with font, content, size, wrapping and alignment |
| Repeated component | Shared Prefab with instance overrides |

Unity UGUI does not include a general-purpose rounded-rectangle drawing component.
Use a shared 9-slice background or a project-approved shape solution. Do not pretend
an untextured Image can draw rounded corners. Reconstruct simple geometry faithfully;
do not substitute a similar icon for a source vector.

Preview before export (source image must match the root frame and source scale):

```bash
python scripts/preview_bboxes.py source.png figma_asset_manifest.json qa/bbox/source.png --source-scale 1
python scripts/extract_png_asset.py source.png icon_back.png --x 100 --y 200 --width 32 --height 32 --scale-factor 3
```

`source.png` and `figma_asset_manifest.json` here denote task input files. A 3x
source uses `--source-scale 3`; bbox still uses design units. Output is
`round(width * scaleFactor)` × `round(height * scaleFactor)`. Never auto-trim,
recenter, shrink or remove intentional transparent padding. These scripts use
Python round (ties to even); prefer export sizes with integer pixel products.

Export vectors at 2x by default; consider 3x/4x below 64 design units. Re-exporting
from vector adds useful detail. Upsampling a low-resolution screenshot does not
recover detail and is reported as `resampledBeyondSource`. Inspect at final display
size and seek a better source when it remains blurry.

For flattened art use a measured L-mode alpha matte at source crop pixel size:

```bash
python scripts/extract_png_asset.py source.png deco_glow.png --x 0 --y 0 --width 160 --height 160 --mask matte.png --background '#ffffff' --scale-factor 2
```

Mask white = opaque, gray = partial alpha, black = transparent. The matte replaces
alpha, so use it only when it represents the complete desired alpha, including any
existing transparency. With known uniform background, recover straight RGB as
`(observed - (1-alpha)*background) / alpha`. Tiny alpha amplifies quantization.
This is an explicit sRGB-channel compositing assumption; nonlinear/unknown/gradient
backgrounds require native export or a separately verified segmentation workflow.
Preserving an existing transparent source requires no mask.

Do not auto-key all similarly colored pixels: it can erase white icons and soft
shadows. If a reliable matte is unavailable, obtain native export or use an available
image editing tool with fixed canvas, shape, position and color constraints, then
verify fidelity and alpha again. Failed extraction is not a completed asset.
