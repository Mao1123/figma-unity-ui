# Source-faithful reconstruction and acceptance

## Preserve the visual contract

Default to strict reproduction. A screenshot or Figma frame is the visual truth;
native UGUI, TMP and Prefabs are implementation choices, not permission to redesign.
Do not replace source icons with icon libraries, procedural approximations, emoji,
AI-generated alternatives or demo assets. Never replace a brand mark with a generic
symbol. Fonts, weight, tracking, line height, gradients, shadows, highlights,
materials, translucency, radii and chart segments all belong to the contract.
Rebuild geometry from measured contours and parameters, then compare it to source.
Use the original vector or transparent export whenever available.

Flattened backgrounds may remain independent raster art, but remove foreground
labels/controls without changing underlying art. Do not use a whole-screen screenshot
as the final Screen. If hidden background cannot be recovered reliably, record the
missing source and keep that asset unresolved. Generative editing is not inherently
faithful; use it only within source-preserving constraints and never approve invented
detail without explicit user authorization. Upscaling does not recover detail.

## Before implementation

1. Preserve the source file and SHA-256, source dimensions, root node/file identity,
   expected state/data, reference resolution and capture configuration. For screenshot
   input use its native dimensions; do not silently convert 941×1672 into 1080×1920.
2. Inventory every visible element: source node or crop bounds, original asset/font,
   measured visual parameters, implementation method and unresolved dependencies.
   Distinguish `native_export`, `source_extraction`, `measured_reconstruction` and
   `authorized_substitution`. Synthetic node IDs must be labeled local.
3. Define a region for every small icon/logo and major panel/background/text/chart
   area. Overlap is allowed. Include all screen pixels in the global comparison;
   local regions prevent a tiny wrong icon disappearing in the global average.
4. Default exact acceptance is threshold 0, changed ratio 0. Rendering tolerances
   require an explicit, recorded agreement before evaluation. Never tune a threshold
   to the observed result or use ratio 1.0 as a fidelity acceptance condition.

Store the inventory and decisions in `visual_fidelity_report.json` next to the two
existing manifests; do not add unsupported fields to those strict schemas. Include
`source`, `capture`, `acceptance`, `elements`, `authorizedChanges`, `regions`,
`technicalStatus`, `alphaStatus`, `visualStatus`, `unresolvedDifferences` and
`comparisonReport`. Each element includes a source reference, bounds, method,
output path, review evidence and status. Authorization records quote the user's
actual approval; a tool outage or unavailable source is not approval.

## Material and alpha review

Open each transparent asset on checkerboard, black and white. Compare its contour,
interior/highlight detail, edge softness and full shadow/glow to the source crop.
Composite the extracted layer back onto the matching source background when known.
Deleting white pixels to make corners transparent can erase anatomy, highlights,
white icon strokes and soft edges. A numerical Alpha PASS cannot detect that loss.
Do not dismiss a fringe flag as intentional without visual/source evidence.

9-slicing must preserve the original radius, border, padding and effects. Do not
slice nonuniform illustrations or distort gradients to save textures. Keep colors
neutral on precolored sprites unless source tint requires otherwise: tint multiplication,
color space, compression and texture settings can shift the palette.

## Unity capture and correction loop

Capture actual Unity rendering with graphics enabled, correct root dimensions,
CanvasScaler, camera, color space, alpha compositing and the same visible data/state.
Freeze timers and animations for comparison. A Null graphics device, solid grey
image, cropped screen or synthetic preview is not evidence of a successful render.
Verify loaded sprites and actual Chinese glyphs, not merely non-null font references.
Match typography and wrapping; an available fallback font is not an approved substitute.

Use the comparator from the skill directory with task files:

```bash
python scripts/compare_images.py reference.png unity.png --exact --regions regions.json --diff qa/diff.png --overlay qa/overlay.png --report qa/comparison.json
```

`regions.json` is an array of objects with unique `name` plus integer `x`, `y`,
`width`, `height` in reference pixels, for example:

```json
[{"name":"brand","x":20,"y":20,"width":100,"height":60},
 {"name":"back_icon","x":20,"y":120,"width":32,"height":32}]
```

Dimensions must match; the tool never resizes or aligns inputs. All regions use
the same locked tolerance. It produces global/per-region metrics, crops, absolute
diff and blend overlay. Exit 0 is a **numerical** pass only; review actual images
at normal size and enlarged scale. Diff metrics cannot decide semantic equivalence.

Inspect and correct in order: background/materials, branding/illustrations, spacing
and geometry, icons, typography, chart segments/states, then interaction/resolution.
Re-capture after changes; keep every unresolved discrepancy. A solid ring is not a
segmented completion chart; changing a tab label is not a complete chart mode switch.
Reusable Prefabs must actually be instantiated where repeated, not merely exported
unused beside a duplicated hierarchy. Technical acceptance includes real interaction
tests, independent of the visual result.

## Completion semantics

Report technical, alpha and visual status separately, with source/capture links and
remaining differences. Exact PASS requires zero rendered pixel differences and no
unresolved source/review items. A tolerated result must state the tolerance and must
not be called pixel-identical. No capture means NOT_TESTED. Unrecoverable material
means BLOCKED for that element; continue independent work and ask for the specific
missing source. Figma quota failures mean remote reconstruction is pending; they
do not authorize simplifying Unity. Never say fully completed merely because a
prefab exists, compilation passes or an empty Figma file was created.
