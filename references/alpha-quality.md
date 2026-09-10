# Alpha is a delivery gate

A PNG is rectangular but a circular object is not. A circle's interior is usually
255 alpha, antialiased edge 1–254, exterior 0. Four corner **pixels** must be exactly
0 unless designed glow/shadow reaches them. Soft content touching any edge is a
clipping risk even at alpha 1. Never trim to hide this risk.

Run the audit with the asset manifest, which supplies per-asset policy. Opaque
backgrounds are permitted only with `alphaRequired:false` and a design reason in
`notes`. Explicit `alphaPolicy` exceptions require `reason`; list only intentionally
touched sides in `allowedTouchingEdges`, and set `allowCornerAlpha` only for actual
corner effects. The audit still rejects a wholly opaque rectangle for transparency.

The report includes dimensions, bytes, original mode, RGBA, channel presence,
corner alpha in TL/TR/BL/BR order, each edge's maximum and mean, exclusive-right/
bottom nontransparent bbox, four touching flags, rectangle risk and color-fringe
candidates. Empty assets, RGB/indexed PNGs, wrong dimensions, unapproved touched
edges and transparency failure are errors. Convert indexed PNG to RGBA first.

Fringe detection compares semitransparent pixels against opaque-core median color,
looking for white, black, blue, purple or an optional known `backgroundColor`.
It is heuristic: it can flag intended outlines/shadows, miss multicolor contamination,
and cannot infer a correct matte. Assets with no opaque core need especially careful
visual review. It does not automatically change pixels.

CLI: exit 0 = numerical checks passed (may include REVIEW); 1 = asset failure;
2 = invocation/input failure. `PASS` is not final visual approval. Review all
`possible_color_fringe` candidates before delivery and record a reason for an
intentional effect. Do not relax alpha policy merely to silence failure.

Audit automatically writes four views per asset under an isolated asset directory:

```text
qa/000_icon_back/
  checkerboard/icon_back_checkerboard.png
  black/icon_back_black.png
  white/icon_back_white.png
  bbox/icon_back_bbox.png
```

`generate_alpha_preview.py icon_back.png --output qa` writes these four categories
directly under `qa`. Do not audit the preview images as production assets.

Actually open all three background views and bbox overlay. Inspect white/black
halos, rectangular remnants, colored edge contamination, missing parts, clipped
glow and preserved padding. Compare the extracted asset composited onto the source
background with its source crop. Store visual reviewer conclusions in the delivery
report alongside the numerical report. Approve only when both pass.
