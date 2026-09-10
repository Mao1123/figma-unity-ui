// MIT. Creates real Unity assets via Editor APIs; never writes prefab YAML.
#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using TMPro;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

namespace FigmaUnityUI
{
    [Serializable] public class UINode
    {
        public string id, figmaNodeId, parentId, name, kind, assetNodeId, text, color, prefabPath, layout, mask;
        public BoundsData bounds;
        public float fontSize = 32, spacing;
        public int[] padding;
        public bool nineSlice;
    }
    [Serializable] public class UIManifest
    {
        public int schemaVersion;
        public string screenName, figmaNodeId, unityPrefab, fontAsset;
        public float[] referenceResolution;
        public float matchWidthOrHeight = .5f;
        public UINode[] nodes;
    }
    public static class FigmaUIPrefabBuilder
    {
        public const string UIPath = "Assets/UI/FigmaSync/figma_ui_manifest.json";
        const string CommonButton = "Assets/UI/Prefabs/Buttons/UI_Button_Base.prefab";
        [MenuItem("Tools/Figma UI/Build Default Screen")]
        public static void BuildDefault() { Build(UIPath, FigmaUIAssetImporter.ManifestPath); }

        static Color ColorOf(string html, Color fallback)
        {
            if (string.IsNullOrEmpty(html)) return fallback;
            if (!ColorUtility.TryParseHtmlString(html, out var c)) throw new InvalidDataException("Invalid color " + html);
            return c;
        }
        static GameObject Rect(string name, Transform parent)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false); return go;
        }
        static void Stretch(RectTransform r)
        {
            r.anchorMin = Vector2.zero; r.anchorMax = Vector2.one;
            r.offsetMin = r.offsetMax = Vector2.zero;
        }
        static Image AddImage(GameObject go, Color color)
        {
            var image = go.AddComponent<Image>(); image.color = color; image.raycastTarget = false; return image;
        }
        static void Save(GameObject go, string path)
        {
            FigmaUIAssetImporter.SafeAssetPath(path);
            if (!path.EndsWith(".prefab", StringComparison.Ordinal)) throw new InvalidDataException("Expected prefab path");
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            if (PrefabUtility.SaveAsPrefabAsset(go,path) == null) throw new IOException("Prefab save failed: " + path);
        }
        static void EnsureButton(TMP_FontAsset font, string path)
        {
            if (File.Exists(path)) return; // Project customizations take precedence.
            var root = Rect("UI_Button_Base", null);
            try
            {
                var bg = Rect("Background",root.transform); Stretch((RectTransform)bg.transform);
                var image = AddImage(bg,new Color(.08f,.38f,.43f)); image.raycastTarget = true;
                var icon = Rect("Icon",root.transform); var ir = (RectTransform)icon.transform;
                ir.anchorMin = ir.anchorMax = new Vector2(0,.5f); ir.anchoredPosition = new Vector2(40,0); ir.sizeDelta = new Vector2(32,32);
                AddImage(icon,Color.white); icon.SetActive(false);
                var label = Rect("Label",root.transform); Stretch((RectTransform)label.transform);
                var tmp = label.AddComponent<TextMeshProUGUI>(); tmp.font = font; tmp.text = "Button";
                tmp.fontSize = 32; tmp.alignment = TextAlignmentOptions.Center; tmp.raycastTarget = false;
                var button = root.AddComponent<Button>(); button.targetGraphic = image; button.transition = Selectable.Transition.ColorTint;
                var colors = button.colors; colors.highlightedColor = new Color(.9f,1,1); colors.pressedColor = new Color(.65f,.8f,.8f);
                colors.selectedColor = new Color(.8f,1,1); colors.disabledColor = new Color(.5f,.5f,.5f,.5f); button.colors = colors;
                Save(root,path);
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }

        public static void Build(string uiPath, string assetsPath)
        {
            var data = JsonUtility.FromJson<UIManifest>(File.ReadAllText(FigmaUIAssetImporter.SafeAssetPath(uiPath)));
            if (data == null || data.schemaVersion != 1 || data.nodes == null || data.referenceResolution == null || data.referenceResolution.Length != 2 ||
                data.referenceResolution[0] <= 0 || data.referenceResolution[1] <= 0) throw new InvalidDataException("Invalid UI manifest");
            FigmaUIAssetImporter.SafeAssetPath(data.unityPrefab);
            // Avoid silently overwriting an existing authored screen.
            if (File.Exists(data.unityPrefab)) throw new IOException("Screen already exists. Review changes and choose a new unityPrefab path or explicitly replace through Editor workflow.");
            var font = string.IsNullOrEmpty(data.fontAsset) ? TMP_Settings.defaultFontAsset : AssetDatabase.LoadAssetAtPath<TMP_FontAsset>(FigmaUIAssetImporter.SafeAssetPath(data.fontAsset));
            if (font == null) throw new InvalidDataException("Missing TMP font; import TMP Essential Resources or set fontAsset");
            var entries = new Dictionary<string,AssetEntry>();
            foreach (var a in FigmaUIAssetImporter.Read(assetsPath).assets) entries.Add(a.nodeId,a);
            var ids = new HashSet<string>();
            foreach (var n in data.nodes)
            {
                if (!ids.Add(n.id) || n.bounds == null || n.bounds.width <= 0 || n.bounds.height <= 0) throw new InvalidDataException("Duplicate id or invalid bounds");
                if (Array.IndexOf(new[]{"Frame","Image","Text","Button","Viewport","Instance"},n.kind)<0) throw new NotSupportedException(n.kind);
                if (!string.IsNullOrEmpty(n.assetNodeId) && (!entries.ContainsKey(n.assetNodeId) || AssetDatabase.LoadAssetAtPath<Sprite>(entries[n.assetNodeId].unityPath)==null))
                    throw new InvalidDataException("Missing Sprite: " + n.assetNodeId);
                if (n.kind == "Instance" && AssetDatabase.LoadAssetAtPath<GameObject>(FigmaUIAssetImporter.SafeAssetPath(n.prefabPath)) == null)
                    throw new InvalidDataException("Missing prefab instance source");
            }
            var buttonPath = Path.GetDirectoryName(Path.GetDirectoryName(data.unityPrefab)).Replace('\\','/') + "/Buttons/UI_Button_Base.prefab";
            EnsureButton(font,buttonPath);
            var root = Rect("Screen_"+data.screenName,null);
            try
            {
                root.AddComponent<Canvas>().renderMode = RenderMode.ScreenSpaceOverlay;
                root.AddComponent<GraphicRaycaster>();
                var scaler = root.AddComponent<CanvasScaler>(); scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
                scaler.referenceResolution = new Vector2(data.referenceResolution[0],data.referenceResolution[1]);
                scaler.referencePixelsPerUnit = 100; scaler.matchWidthOrHeight = data.matchWidthOrHeight;
                ((RectTransform)root.transform).sizeDelta = scaler.referenceResolution;
                var objects = new Dictionary<string,GameObject>();
                var remaining = new List<UINode>(data.nodes);
                while (remaining.Count > 0)
                {
                    bool progress = false;
                    foreach (var n in remaining.ToArray())
                    {
                        if (!string.IsNullOrEmpty(n.parentId) && !objects.ContainsKey(n.parentId)) continue;
                        var parent = string.IsNullOrEmpty(n.parentId) ? root.transform : objects[n.parentId].transform;
                        GameObject go;
                        if (n.kind == "Button" || n.kind == "Instance")
                        {
                            string path = n.kind == "Button" ? buttonPath : n.prefabPath;
                            go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(path),parent);
                            go.name = n.name;
                        }
                        else go = Rect(n.name,parent);
                        var rect = go.GetComponent<RectTransform>();
                        if (rect == null) throw new InvalidDataException("UI instance needs RectTransform");
                        rect.anchorMin = rect.anchorMax = rect.pivot = new Vector2(0,1);
                        rect.anchoredPosition = new Vector2(n.bounds.x,-n.bounds.y);
                        rect.sizeDelta = new Vector2(n.bounds.width,n.bounds.height);
                        Image image = null;
                        if (n.kind == "Image") image = AddImage(go,ColorOf(n.color,Color.white));
                        if (n.kind == "Viewport") { var raw = go.AddComponent<RawImage>(); raw.color = ColorOf(n.color,new Color(.2f,.2f,.2f)); raw.raycastTarget=false; }
                        if (n.kind == "Text")
                        {
                            var tmp = go.AddComponent<TextMeshProUGUI>(); tmp.font=font; tmp.text=n.text;
                            tmp.fontSize=n.fontSize; tmp.color=ColorOf(n.color,Color.black); tmp.raycastTarget=false;
                        }
                        if (n.kind == "Button")
                        {
                            var tmp = go.transform.Find("Label").GetComponent<TextMeshProUGUI>(); tmp.font=font; tmp.text=n.text;
                            if (!string.IsNullOrEmpty(n.assetNodeId))
                            {
                                image=go.transform.Find("Icon").GetComponent<Image>(); image.gameObject.SetActive(true);
                                var labelRect=(RectTransform)tmp.transform; labelRect.offsetMin=new Vector2(64,0);
                            }
                        }
                        if (image != null && !string.IsNullOrEmpty(n.assetNodeId))
                        {
                            var entry=entries[n.assetNodeId]; image.sprite=AssetDatabase.LoadAssetAtPath<Sprite>(entry.unityPath);
                            if (n.nineSlice && !entry.nineSlice) throw new InvalidDataException("Sliced Image needs border asset");
                            image.type=n.nineSlice ? Image.Type.Sliced : Image.Type.Simple;
                            image.preserveAspect=!n.nineSlice;
                            if(n.kind=="Button") ((RectTransform)image.transform).sizeDelta=new Vector2(entry.sourceBounds.width,entry.sourceBounds.height);
                        }
                        if (!string.IsNullOrEmpty(n.layout))
                        {
                            HorizontalOrVerticalLayoutGroup group = n.layout=="Horizontal" ? (HorizontalOrVerticalLayoutGroup)go.AddComponent<HorizontalLayoutGroup>() : go.AddComponent<VerticalLayoutGroup>();
                            group.spacing=n.spacing; group.childControlWidth=false; group.childControlHeight=false;
                            group.childForceExpandWidth=false; group.childForceExpandHeight=false;
                            if(n.padding != null && n.padding.Length==4) group.padding=new RectOffset(n.padding[0],n.padding[2],n.padding[3],n.padding[1]);
                        }
                        if(n.mask=="Rect") go.AddComponent<RectMask2D>();
                        if(n.mask=="Sprite") { if(go.GetComponent<Graphic>()==null) throw new InvalidDataException("Sprite Mask needs Graphic"); go.AddComponent<Mask>().showMaskGraphic=false; }
                        objects.Add(n.id,go); remaining.Remove(n); progress=true;
                    }
                    if(!progress) throw new InvalidDataException("Missing parent or hierarchy cycle");
                }
                // Restore manifest sibling order even when parents were listed later.
                foreach(var n in data.nodes) objects[n.id].transform.SetAsLastSibling();
                Canvas.ForceUpdateCanvases();
                LayoutRebuilder.ForceRebuildLayoutImmediate((RectTransform)root.transform);
                Save(root,data.unityPrefab);
                Debug.Log("Figma UI: created "+data.unityPrefab+". Connect viewport camera, input module and application callbacks in the scene.");
            }
            finally { UnityEngine.Object.DestroyImmediate(root); }
        }
    }
}
#endif
