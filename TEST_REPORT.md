# Validation record

Local validation: 2026-09-09, Windows, Python 3.11.9, Pillow 10.4.0.

| Check | Result |
|---|---|
| Circle, 1x/2x/3x/4x, exact alpha-zero corners, stable canvas | PASS |
| Circle with soft shadow, known-white background removal using explicit matte | PASS; alpha byte-for-byte preserved, recomposite error at most 1 channel value |
| Rounded rectangle corner alpha | PASS |
| Ordinary opaque background allowed; same file rejected when transparency required | PASS |
| Both example manifests and generated RGBA files | PASS |
| Unsafe paths, duplicates, bad borders, bad names, scale and unknown fields rejected | PASS |
| Hierarchy cycles and missing cross-manifest asset references rejected | PASS |
| Empty image, RGB image, edge clipping and white/black/blue/purple fringe fixtures | PASS |
| Invalid extraction bbox and background-without-matte rejected | PASS |
| Every Python script --help; image equality and difference exit behavior | PASS |
| Audit CLI, all preview files and source BBox overlay pixels | PASS |
| Reasoned edge exception and incorrect pixel-size detection | PASS |

**12 tests passed, 0 failed.** Reproduce with
`python -m unittest discover -s tests -v` from repository root.

Two original demo assets were also generated and audited through the published
Quick Start commands. All eight checkerboard/black/white/bbox views were opened
and visually reviewed: no rectangular residual background, color fringe or clipped
content. The white panel naturally becomes invisible against pure white except
through its bounds; its black/checkerboard views confirm transparent corners.

Codex's installed `skill-creator/scripts/quick_validate.py` passed using Python
UTF-8 mode. The first attempt hit Windows GBK decoding, resolved by `python -X utf8`;
no change to the official validator was needed. Frontmatter contains only name and
description. Local Markdown links, helper paths and unfinished-marker checks pass.

Local installation under `~/.codex/skills/figma-unity-ui` was loaded from disk,
validated, and its installed audit helper successfully processed both demo assets
with absolute project paths. Codex subsequently exposed `figma-unity-ui` in its
available-skills catalog, confirming discovery and installation.

Unity smoke runner: `tests/UnitySmoke.cs` creates/imports resources in an isolated
Editor test project and checks actual sprites, scaled borders, nested button
prefabs, editable TMP and missing scripts.

**Unity 2022.3.48f1c1 Editor smoke test: PASS.** Two Sprite assets imported;
icon size 96×96 and PPU 300 verified; panel border [40,40,40,40] verified;
Screen_AcupointLearning prefab created with six nested Button instances and eight
TextMeshProUGUI components. Sliced InformationPanel and valid nested prefab source
checked. Hierarchy validator reported zero errors; runner emitted
`FIGMA_UNITY_SMOKE_PASS` and `{ "passed": true, "buttons": 6, "texts": 8 }`.

The first build attempt correctly rejected a missing TMP font because the test
runner did not wait for package import. The runner was fixed to wait for
`AssetDatabase.importPackageCompleted`; the complete rerun passed. Initial
Editor licensing-client diagnostics were followed by successful startup; no
licensing configuration or existing user projects were modified.

This was batch mode with no graphics. Play Mode callbacks, EventSystem input,
multi-resolution visual rendering, live Figma/Unity MCP and Unity 6 were not tested.
These are explicit remaining integration checks, not passed tests.

No official packaging tool was found in the installed skill tooling. The repository
and optional ordinary ZIP are distribution artifacts, not official certification.
