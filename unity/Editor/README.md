# Editor integration

Copy all three `.cs` files together to `Assets/UI/Scripts/Editor` (or an existing
Editor folder). UGUI and TextMeshPro must be available; import TMP Essential
Resources or specify an existing TMP font in the UI manifest.

1. Validate both manifests with the Python tools and inspect Alpha QA.
2. Put accepted assets at their `unityPath`, manifests in `Assets/UI/FigmaSync`.
3. Wait for compilation. Run **Tools → Figma UI → Import Default Asset Manifest**.
4. Run **Tools → Figma UI → Build Default Screen**.
5. Instantiate the saved Screen in a scene; add/configure the scene EventSystem
   according to the active input system. Bind callbacks and the viewport texture.
6. Select the instance and run **Tools → Figma UI → Validate Selected Hierarchy**.
7. Test input, states, aspect ratios, fonts and Console as described in
   [Prefab workflow](../../references/unity-prefabs.md).

Custom manifest paths: invoke the public `Import(path)` and `Build(uiPath,assetsPath)`
methods through an Editor script or an available Unity automation tool. No package
installation, global project settings changes or prefab YAML rewriting occurs.

Builder refuses to overwrite an existing Screen, reuses the existing button base,
and uses actual PrefabUtility nested instances. Imported textures keep GUIDs.
SVG requires a separate supported importer/rasterization path. Generated UI is a
visual foundation; business logic, advanced constraints and 3D content are project work.

These sources compiled and ran in Unity 2022.3.48f1c1: import and prefab-build
smoke tests passed. Unity 6, Play Mode input and multi-resolution rendering remain
unverified. See [test record](../../TEST_REPORT.md). To reproduce the Editor smoke
test, generate assets in a fresh Unity project, copy `tests/UnitySmoke.cs` into its
Editor folder and invoke `FigmaUnityUISmoke.Run` via batch mode. The runner imports
TMP Essential Resources and exits the Editor; use an isolated project only.
