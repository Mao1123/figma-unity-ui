# Third-party notices

This project derives from and references **YYY887/image-to-code-skill**:
https://github.com/YYY887/image-to-code-skill

Reviewed revision: `886c882a05b3c44b27e1ac277d740eb3dc0b1a5b`.
Original license: MIT. Original notice: **Copyright (c) 2026 Donyzh**.
The complete MIT notice is retained in [LICENSE](LICENSE).

`scripts/extract_png_asset.py`, `audit_png_assets.py`, `preview_bboxes.py` and
`compare_images.py` are substantially rewritten adaptations of the upstream
helpers' workflow and algorithms. Fixed-canvas BBox extraction, density metadata,
corner/edge inspection, image-difference measurement and no-trim guidance derive
from that work. `references/slicing.md` and control-plane guidance retain those
substantive concepts with Unity-specific rules.

New work includes grayscale-matte uncompositing, visual QA generation, Unity alpha
policy and fringe heuristics, both versioned schemas and their validator, example
generator, tests, Unity Editor importer/builder/validator, and Figma-to-Unity
documentation. Web layout and CSS-specific conventions were removed. Figma
editable-node principles were redesigned around UGUI and TextMeshPro.

Pillow, NumPy and jsonschema are installed dependencies, not vendored code. Their
respective licenses continue to apply to those distributions. Demo art is original
geometric test artwork created for this repository; no private/commercial assets
or third-party font binaries are included. Figma and Unity are their owners'
trademarks; this project does not imply endorsement.
