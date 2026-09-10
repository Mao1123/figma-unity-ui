# Maintainable UGUI hierarchy

| Figma concept | Unity result |
|---|---|
| Meaningful Frame | GameObject + RectTransform |
| Text | TextMeshProUGUI |
| Image | Image with Sprite |
| Vector | Sprite / supported SVG import |
| Component | Prefab |
| Instance | Prefab instance with overrides |
| Horizontal/Vertical Auto Layout | HorizontalLayoutGroup / VerticalLayoutGroup |
| Scroll area | ScrollRect with viewport and content |
| Rectangular mask | RectMask2D |
| Shape mask | Graphic + Mask |

Collapse organizational-only Figma frames when their effects and constraints can
be preserved. Maintain semantic screen sections. Bounds in the UI manifest are
parent-local design coordinates. Builder uses top-left anchors/pivot and
anchoredPosition `(x,-y)`. Asset sourceBounds remain root-relative. These are
different coordinate spaces, especially for nested frames.

LayoutGroup owns child positions; do not simultaneously drive them with absolute
positions. The basic builder uses fixed child sizes and explicit spacing/padding.
Handle Figma hug/fill, alignment, minimum size and text growth by configuring
LayoutElement/ContentSizeFitter only where needed, avoiding layout feedback loops.
For ScrollRect: create a root, stretched viewport with RectMask2D, content under
viewport, assign viewport/content, scrolling axes and movement settings, and size
content from layout. ScrollRect is an Editor/MCP extension workflow, not a supported
kind in the bundled minimal builder; do not feed unsupported fields to it.

Default button:

```text
Btn_Name (RectTransform, Button)
  Background (Image, raycastTarget=true)
  Icon (Image, raycastTarget=false)
  Label (TextMeshProUGUI, raycastTarget=false)
```

Use ColorTint for Normal/Highlighted/Pressed/Selected/Disabled color variations.
For substantial visual changes, set transition SpriteSwap and SpriteState for
highlighted/pressed/selected/disabled; normal is target Image.sprite. Apply swaps
to Background, not the root if it has no Graphic. Keep labels independent.

The bundled builder creates/reuses `UI_Button_Base.prefab` and creates a Screen
with real nested button instances. Specialized repeated families should become
`UI_CategoryButton`, `UI_IconButton`, `UI_TabButton`, `UI_InfoCard` prefabs or variants
through Editor/MCP. It supports explicit `kind:Instance` plus `prefabPath`; create
the source prefab first. Do not generate redundant families when only one exists.

Use `FigmaUIPrefabBuilder.Build(uiPath, assetPath)` after importing assets, or
**Tools → Figma UI → Build Default Screen**. TMP Essential Resources / a valid
`fontAsset` must exist. Check glyph coverage, fallback fonts, alignment, wrapping,
line height and font weights against source. Builder example defaults are not a
complete typography translator. It refuses existing screen destinations; preserve
hand-authored behavior and use reviewed Editor modifications for resync.

Example contains editable English educational text and a RawImage ModelViewport.
Connect a RenderTexture and camera for actual 3D; do not ship the empty viewport as
completed 3D content. Add one scene EventSystem with the project's active input
module, ensure GraphicRaycaster works, and bind real callbacks. Builder creates
visual controls; it does not implement teaching/navigation business logic.

Run **Validate Selected Hierarchy**; check missing components, sprites, fonts,
references, sliced images and button targets. Then test Play Mode input and five
button states. Capture root resolution and at least two device aspect ratios,
including safe areas and longer localized text. Check out-of-bounds children,
clipped shadow, stacking, Mask/ScrollRect clipping and Console Errors via Unity MCP
or Editor. The validator logs review items and cannot prove visual fidelity,
interactivity or multi-resolution fit automatically.
