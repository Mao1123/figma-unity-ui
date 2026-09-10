# Two versioned contracts

Machine schemas: [assets](figma_asset_manifest.schema.json),
[UI structure](figma_ui_manifest.schema.json), JSON Schema 2020-12. Unknown fields
are rejected to catch typos; extend schema and consumers together when needed.
Examples use fictional node IDs and no remote Figma file.

## Asset manifest (schemaVersion 1)

Required root: schemaVersion, figmaFile (may be empty for local input), rootNodeId,
assets. Each asset requires nodeId, figmaName, assetType, fileName, unityPath,
format (png/svg), scaleFactor (1/2/3/4), sourceBounds (x,y,width,height),
alphaRequired and nineSlice. Optional border, filterMode, notes, backgroundColor,
alphaPolicy. `sourceBounds` uses root-local design units and includes export padding.
`unityPath` is project-relative under Assets, never absolute or traversal.

`border`: [left,bottom,right,top] in design units. `alphaPolicy`: reason plus optional
allowCornerAlpha and allowedTouchingEdges (left/right/top/bottom). Opaque assets
require notes. Filenames must exactly match export naming conversion; duplicate
node IDs and case-insensitive paths are rejected. Categories: bg, panel, btn, icon,
card, deco, illustration. Never classify editable text as an exported asset.

Dimensions are derived from design extent × scale. Validator checks actual RGBA
PNG dimensions when `--project-root` is supplied. It checks SVG file existence,
not vector geometry, external references or rendering correctness. Audit PNGs
separately; successful JSON validation does not imply acceptable alpha.

## UI manifest (schemaVersion 1)

Required: screenName, figmaNodeId, referenceResolution [width,height], unityPrefab,
nodes. Optional fontAsset (project-relative TMP font asset) and matchWidthOrHeight
(0–1, builder default .5). Reference resolution comes from Figma root.

Each node requires id, figmaNodeId, parentId (empty = screen root), name, kind and
bounds. Parent-local top-left bounds preserve the root unit system, never raster
pixel density. Node array order defines sibling order. Cycles, unknown parents and
duplicate sibling names are errors. `assetNodeId` refers to asset manifest nodeId.

Builder kinds: Frame, Image, Text, Button, Viewport, Instance. Optional fields:
text, fontSize, color (#RRGGBB or #RRGGBBAA), nineSlice, prefabPath,
layout (Horizontal/Vertical), spacing, padding [left,bottom,right,top], mask
(Rect/Sprite). Text requires content; Instance requires prefabPath. The compact
schema describes the bundled builder, not every Figma feature. Use project Editor
extensions for anchors, scroll configuration, advanced typography, state sprite
bindings and application logic, documenting the additional contract.

Commands (task filenames are inputs):

```bash
python scripts/validate_manifest.py figma_asset_manifest.json --project-root .
python scripts/validate_manifest.py figma_ui_manifest.json --assets figma_asset_manifest.json
```

Always run Python validation before Unity Editor methods: JsonUtility does not
implement JSON Schema and the Editor scripts only perform essential preflight.
Use `--assets` for cross-manifest references; without it references are not checked.
