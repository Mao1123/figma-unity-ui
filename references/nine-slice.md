# 9-slice without density mistakes

For stretchable Button backgrounds, Panels, Cards, Tabs and Inputs, prefer one
shared sprite and `Image.Type.Sliced`. Do not export each display width separately.
Keep icon and text separate. Border must enclose corners/strokes while leaving a
nonempty stretchable center. Avoid slicing illustrations, irregular textures or
glow whose appearance changes under independent stretching.

Manifest: `nineSlice:true`, `border:[left,bottom,right,top]` in **design units**.
Example: a 96×96 design asset at 2x is 192×192 pixels. Border `[20,20,20,20]`
becomes `[40,40,40,40]` pixels. PPU is 200, Canvas reference PPU 100; visual
border thickness remains 20 design units. Screen Image requests `nineSlice:true`.

Inspect Sprite Editor borders against corner geometry. Preserve transparent
padding intentionally: include it in border measurements. Test narrow, normal
and wide sizes; width/height should not shrink below border sums. Verify corners
stay round, stroke width remains stable, center stretches cleanly and shadow is
not clipped. Do not use sliced sprites as Button icons.

The schema rejects borders consuming the full source center; Unity importer scales
the border and the builder enables Sliced on the consuming Image. Inspector-only
border entry uses actual texture pixels, not the unscaled manifest values.
