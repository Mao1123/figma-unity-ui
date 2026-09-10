# Figma → Unity UI

A Codex skill for turning Figma/UI designs into Unity-ready transparent assets,
validated manifests, Sprite import settings, 9-slice UI and reusable UGUI prefabs.
面向 Unity 2022.3 LTS、Unity 6、UGUI 与 TextMeshPro。

## What it does

Converts source designs into independent assets and editable, component-based UI.
Text remains TMP, simple geometry remains native/shared geometry, repeated UI
becomes Prefabs, complex visuals become PNG/SVG, and 3D areas become viewports.
The whole screen screenshot is reference material only.

## Features

- Fixed BBox extraction with 1x/2x/3x/4x output (default 2x), no automatic trim.
- Explicit matte-based background removal preserving soft alpha and padding.
- Alpha audit for corners, edges, empty assets, wrong dimensions, rectangular
  backgrounds and possible white/black/blue/purple color contamination.
- Automatic checkerboard, black, white and bbox QA previews.
- Separate versioned asset and hierarchy manifests with JSON Schema validation.
- Unity Editor Sprite importer, real Prefab builder and hierarchy validator.
- Original 1080×1920 medical teaching example with no commercial/private art.

## Architecture

```text
UI reference / Figma nodes
  → structure analysis and classification
  → fixed BBox + native export / explicit mask
  → RGBA PNG or source SVG + Alpha Audit + visual QA
  → figma_asset_manifest.json + figma_ui_manifest.json
  → Unity Assets + TextureImporter + Sprite borders
  → reusable Prefabs + component-based Screen
  → Unity rendering, interaction and resolution QA
```

`SKILL.md` is the concise control plane. Details live in `references/`; Python tools
in `scripts/`; Editor C# in `unity/Editor/`; examples in `examples/`.

## Installation

Clone the repository into your Codex skills directory:

```bash
git clone https://github.com/Mao1123/figma-unity-ui.git ~/.codex/skills/figma-unity-ui
cd ~/.codex/skills/figma-unity-ui
python -m pip install -r requirements.txt
```

PowerShell equivalent (Python 3.10+):

```powershell
git clone https://github.com/Mao1123/figma-unity-ui.git "$HOME/.codex/skills/figma-unity-ui"
Set-Location "$HOME/.codex/skills/figma-unity-ui"
python -m pip install -r requirements.txt
```

If the destination exists, inspect it before updating. If you use a custom
`CODEX_HOME`, use its `skills/figma-unity-ui` directory. Reopen a Codex task if the
new skill is not yet discoverable. No unverified `npx` installer is advertised.

## Quick Start

Run from the cloned skill folder. The example generator writes to a fresh isolated
folder, refusing to overwrite generated files. This folder is an Assets staging
tree; open/copy it into a real Unity project for Editor execution.

```bash
python scripts/create_example_assets.py --project-root test-output/demo
python scripts/validate_manifest.py test-output/demo/Assets/UI/FigmaSync/figma_asset_manifest.json --project-root test-output/demo
python scripts/validate_manifest.py test-output/demo/Assets/UI/FigmaSync/figma_ui_manifest.json --assets test-output/demo/Assets/UI/FigmaSync/figma_asset_manifest.json
python scripts/audit_png_assets.py --manifest test-output/demo/Assets/UI/FigmaSync/figma_asset_manifest.json --project-root test-output/demo --qa-dir test-output/qa --report test-output/alpha_report.json
python -m unittest discover -s tests -v
```

Open the generated QA views. Exit code 0 means numerical checks passed; visual
approval still requires inspecting every transparent asset. The generated demo
assets are intentionally simple, original geometry for pipeline testing.

## Codex Usage

```text
使用 $figma-unity-ui 将当前 Figma 页面切分成 Unity UGUI 可用素材，导出透明 PNG，并直接同步到我的 Unity 项目。

使用 $figma-unity-ui 检查这些圆形 UI 切图，清理背景残留并执行 Alpha QA。

使用 $figma-unity-ui 根据当前 Figma Frame 在 Unity 中创建 Prefab 和 Screen Hierarchy。
```

Supply the design selection/link or image, and the Unity project folder for direct
integration. Codex resolves helpers relative to the installed skill and outputs
relative to the chosen project. The skill does not require both MCPs for local QA.

## Figma MCP

Use available Figma tools to inspect actual nodes, components, instances, Auto
Layout, text, vectors, rectangles, images, masks, slices, variables and export
settings. Root dimensions drive CanvasScaler. `export/*` nodes are individual
assets. Native vector export at density is preferred over upsampling screenshots.
See [Figma workflow](references/figma-workflow.md).

## Unity MCP

When connected, use Unity automation to invoke Editor import/build methods, inspect
Hierarchy, check Console and capture Game View. Tool names are discovered from the
installed integration. Without Unity MCP, the same methods are accessible from
Editor menus. Without an Editor, deliver staged files and clearly report runtime
validation as pending. No handwritten prefab YAML is needed.

## Asset Naming

`export/icon/back` → `icon_back.png`; `export/panel/ai_assistant` →
`panel_ai_assistant.png`; `export/btn/category_selected` →
`btn_category_selected.png`. English lowercase snake_case, no spaces, Chinese,
`(1)`, `copy` or numeric suffixes. Custom project folders are supported under
`Assets/`. [Full mapping](references/figma-workflow.md).

## Alpha QA

Required fields include `has_alpha_channel`, `transparent_bg_ok`, `corner_alpha`,
`edge_alpha`, `nontransparent_bbox`, four `touching_*_edge` flags,
`possible_background_rectangle`, `possible_color_fringe`, size, bytes and RGBA mode.
Circle corners must be alpha 0 unless an explicit, reasoned shadow/glow exception
applies. Partial-alpha pixels count as content. Opaque rectangles need manifest
permission and notes. Never change transparency intent just to pass an audit.

Every audit generates `checkerboard/`, `black/`, `white/` and `bbox/` inside a
per-asset QA folder to avoid filename collisions. Fringe findings are REVIEW
hypotheses, not automatic defects; inspect and record conclusions. No trim occurs.
See [Alpha quality](references/alpha-quality.md) and [slicing](references/slicing.md).

## Unity Import

Copy `unity/Editor/*.cs` into an Editor folder in the Unity project. Put manifests
at `Assets/UI/FigmaSync` and assets at their manifest paths. After Python QA, run
**Tools → Figma UI → Import Default Asset Manifest**, then **Build Default Screen**.
Import TMP Essential Resources or set `fontAsset` first. Finally instantiate the
Screen prefab and run **Validate Selected Hierarchy**.

Settings: Sprite, Single, Full Rect, Alpha Is Transparency, Clamp, no mipmaps,
Bilinear by default. PPU = 100 × export scale; RectTransform retains design size.
Existing platform overrides may affect size and must be reviewed. Default folders
include Backgrounds, Panels, Buttons, Icons, Cards, Decorations, Illustrations,
Source, Prefabs, Scripts and FigmaSync. [Editor setup](unity/Editor/README.md).

## 9-Slice

Reusable backgrounds use Sprite Border and Image Sliced. Manifest borders use
design units in left/bottom/right/top order; importer multiplies them by export
scale. This preserves corner thickness across density and display size. Do not
stretch icons or illustrations as sliced backgrounds. [Details](references/nine-slice.md).

## Manifest

- [Asset example](examples/figma_asset_manifest.example.json): identity, export
  name, destination, scale, root-relative source bounds, alpha intent and borders.
- [UI example](examples/figma_ui_manifest.example.json): 1080×1920 reference,
  parent-local hierarchy, assets, editable text, layouts and prefab destination.
- [Schema guide](references/manifest-schema.md): supported fields and validation.

Validate before Editor import. `--project-root` checks files/dimensions;
`--assets` enables cross-manifest references. Schemas reject unknown fields.

## Example

```text
Screen_AcupointLearning
  Background
  Header
    Btn_Back
    Title
  Navigation
    Btn_Acupoint
    Btn_Meridian
    Btn_Muscle
  Content
    ModelViewport
    InformationPanel
      Description
  Footer
    Btn_Previous
    Btn_Next
```

Fictional Figma node `123:456` → `export/icon/back` → 96×96 `icon_back.png`
at 3x → Sprite PPU 300 → a 32×32 Icon under `Btn_Back`.
Node `123:457` → panel sprite → 2x borders → sliced InformationPanel.
Buttons are nested instances of `UI_Button_Base.prefab`, with TMP labels.
The builder writes `Assets/UI/Prefabs/Screens/Screen_AcupointLearning.prefab`.
The viewport requires a project camera/RenderTexture; button events require
application callbacks. This is a UI pipeline example, not a medical simulator.

## Tests and Validation

The initial local run passes 12 behavioral tests covering the five requested
representative cases plus density, clipping, empty/RGB images, colored fringe,
unsafe paths, duplicate IDs, invalid borders, hierarchy cycles and CLI behavior.
Run the test command above to reproduce. [Test record](TEST_REPORT.md).

Unity 2022.3.48f1c1 also passed the isolated Editor smoke test: two sprites,
scaled borders, a Screen prefab, six nested buttons, eight editable TMP texts and
zero hierarchy-validator errors. The smoke runner waits for TMP package import
completion before building. Play Mode and multi-resolution rendering remain untested.

The installed skill is checked using the available Codex `quick_validate.py` and
its installed scripts are executed against demo assets. Codex subsequently listed
`figma-unity-ui` among available skills, confirming discovery. No official
packaging tool is bundled here; ordinary ZIP distribution must not be described
as official package certification.

## Limitations

- Unity 2022.3.48f1c1 compilation and Editor import/build passed. Unity 6, Play Mode,
  device rendering, live Figma reads and live Unity MCP are not exercised. Those
  environments still require their own integration checks.
- Flattened unknown backgrounds cannot be reliably uncomposited without a correct
  matte. Upscaling cannot invent lost detail. Color-fringe detection is heuristic.
- SVG export is supported by the contract; the bundled PNG TextureImporter rejects
  SVG. Use a verified project vector importer or rasterize first.
- Builder supports a documented subset. Advanced typography, hug/fill constraints,
  ScrollRect setup, SpriteState binding, safe areas and business events require
  project-specific Editor/MCP work.
- First-build generation refuses existing Screen destinations. Ongoing sync must
  preserve GUIDs, instance overrides and authored behavior through reviewed edits.

## Credits

Derived from [YYY887/image-to-code-skill](https://github.com/YYY887/image-to-code-skill),
original copyright **2026 Donyzh**, at commit
`886c882a05b3c44b27e1ac277d740eb3dc0b1a5b`. Fixed-canvas slicing, alpha inspection,
bbox preview and image comparison concepts were retained and rewritten for Unity.
See [migration notes](references/upstream-migration.md) and
[third-party notices](THIRD_PARTY_NOTICES.md). Original work is not claimed as
solely authored by this repository's maintainer.

## License

[MIT](LICENSE), preserving the upstream copyright and permission notice.
