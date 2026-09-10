# Unity import

Target Unity 2022.3 LTS and Unity 6 with UGUI and TextMeshPro. Copy the three
`unity/Editor/*.cs` files to an Editor directory under Assets, or use the example
generator in an isolated folder. Honor existing UI directory conventions. Default:

```text
Assets/UI/
  Backgrounds/ Panels/ Buttons/ Icons/ Cards/ Decorations/ Illustrations/ Source/
  Prefabs/Common/ Prefabs/Buttons/ Prefabs/Panels/ Prefabs/Screens/
  Scripts/Runtime/ Scripts/Editor/ FigmaSync/
```

Validate asset manifest using `--project-root`, run Alpha QA, copy accepted PNGs
without replacing existing `.meta`, then call `FigmaUIAssetImporter.Import(path)`
from Editor/MCP or use **Tools → Figma UI → Import Default Asset Manifest**.
The default manifest path is `Assets/UI/FigmaSync/figma_asset_manifest.json`.
Custom folders work through the public path-taking method.

Importer settings: Sprite / Single / FullRect, FromInput alpha, alphaIsTransparency,
Clamp, no mipmaps, NPOT None, Bilinear (per-asset Point/Trilinear override),
Uncompressed for initial QA. Max texture size covers the source pixel extent.
Existing platform-specific overrides are preserved and may downscale; the importer
detects resulting size mismatch. Review platform compression/atlas padding after
initial QA and repeat device alpha/9-slice checks after optimization.

`spritePixelsPerUnit = 100 * scaleFactor`, with Canvas referencePixelsPerUnit 100.
Set RectTransform from design bounds, not PNG pixels. This also keeps native-size
operations and Image sliced border thickness consistent at 2x/3x/4x. If the project
uses another reference PPU, adapt both together. Never blindly call SetNativeSize
with an unrelated PPU. Border order is left,bottom,right,top, multiplied by scale.

SVG files are source/vector deliverables; standard TextureImporter cannot import
SVG as a Sprite. Use a project-approved compatible SVG/vector package after
checking its installed API, or rasterize from the original vector at export density
and update manifest format/path. The bundled importer explicitly rejects SVG;
it does not install packages or claim universal SVG support.

References: [Unity TextureImporter](https://docs.unity3d.com/2022.3/Documentation/ScriptReference/TextureImporter.html),
[CanvasScaler](https://docs.unity3d.com/Packages/com.unity.ugui@2.0/manual/script-CanvasScaler.html).
Compilation and Editor import/build passed on Unity 2022.3.48f1c1. Unity 6 and
rendering/input validation remain project integration checks; see TEST_REPORT.md.
