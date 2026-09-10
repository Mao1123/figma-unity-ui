# Upstream research and migration decisions

Reviewed all upstream files at revision
`886c882a05b3c44b27e1ac277d740eb3dc0b1a5b`: SKILL.md, README.md, LICENSE,
requirements.txt, both references, all four scripts and agents/openai.yaml.
The installed local image-to-code skill differs from this GitHub revision; the
requested GitHub source is the authoritative migration reference.

| Upstream area | Decision and rationale |
|---|---|
| Fixed x/y/width/height crop | Retain; separate design units and source pixel density |
| Scaling PNG without changing display size | Retain; map display size to RectTransform and PPU |
| No trim, source fidelity, transparent padding | Retain as invariant |
| Corner/edge alpha audit | Rewrite per-asset policy; opaque rectangular backgrounds can pass |
| corners/floodfill background removal | Replace with explicit matte/unmatting; color key can destroy shadows and leave fringe |
| Image comparison | Adapt to black/white composites plus alpha; reject size and threshold mismatches |
| Bounding-box preview | Adapt to asset manifest and root-relative coordinates |
| Figma editable export reference | Retain semantic native text/vector principle; reverse direction toward Unity |
| 750px baseline, CSS sizes, DOM and responsive wrappers | Remove; Figma root + CanvasScaler + RectTransform replace them |
| layers.manifest.json | Replace with two versioned Unity contracts |
| Agent metadata | Rewrite for targeted Figma/Unity discovery |

Upstream requirements were Pillow and NumPy. This project adds jsonschema for
executable contract checking. Original MIT copyright is preserved. The project
does not copy the full source skill or its Web output model.
