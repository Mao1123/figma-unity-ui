# Figma workflow and capability negotiation

Use the installed Figma integration's applicable prerequisite skills before reading,
generating or modifying designs. Discover real MCP capabilities rather than inventing
an endpoint. Read the selected root Node/Frame and descendants with pagination;
collect Component, Instance, Auto Layout, Text, Vector, Rectangle, Image, Mask,
Slice, Variables and Export Settings wherever exposed. Resolve instance overrides,
variable modes, visibility, blend effects, clipping and font availability. Fetch
root screenshot only as a visual cross-check. If an API omits metadata, report it.

Do not export text in button assets. Separate label and icon from backgrounds.
Preserve source node IDs for traceability. `export/*` denotes an independently
exportable Unity asset; it does not mean the parent and children should both be
duplicated into overlapping sprites. Prefer native vector exports over screenshot
segmentation. Respect explicit Slice bounds or create an export wrapper when needed
to preserve effect padding. PNG scale lives in Export Settings, not layout size.

| Figma name | File | Default folder |
|---|---|---|
| export/bg/main | bg_main.png | Assets/UI/Backgrounds |
| export/panel/ai_assistant | panel_ai_assistant.png | Assets/UI/Panels |
| export/btn/category_selected | btn_category_selected.png | Assets/UI/Buttons |
| export/icon/acupoint | icon_acupoint.png | Assets/UI/Icons |
| export/card/information | card_information.png | Assets/UI/Cards |
| export/deco/header | deco_header.png | Assets/UI/Decorations |
| export/illustration/anatomy | illustration_anatomy.png | Assets/UI/Illustrations |

Use meaningful English words; lowercase snake_case, no spaces, Chinese, `(1)`,
`copy`, arbitrary numeric suffixes. The validator conservatively disallows all
digits in exported asset names. Resolve collisions semantically before export.
Existing project folders override these defaults. SVG keeps the same stem.

On sync, compare by node ID, not mutable display name. Stage proposed assets and
manifest changes, run QA, then update managed Unity assets while preserving `.meta`
GUIDs. Do not delete orphan assets, custom scripts, events or hand-edited prefabs
automatically. Record removed nodes for review and use prefab overrides/variants.
The included builder intentionally refuses to overwrite an existing Screen; it is
a first-build tool. Ongoing sync uses inspected Editor/MCP edits and reviewed diffs.

If only a screenshot is available, create a measurement/classification plan and, if
requested and tools permit, reconstruct editable Figma shapes/text before export.
Do not claim synthetic example node IDs are from a real remote file.

Tool quota or connection failure does not authorize substituting visuals. Continue
source-faithful local work where possible, retain unresolved original assets, and
report remote generation separately. Creating an empty file is not reconstructing
the design. Apply [visual fidelity](visual-fidelity.md) before fallback execution.
