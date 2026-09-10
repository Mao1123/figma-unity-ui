// MIT. Copyright (c) 2026 Mao1123. See repository LICENSE and THIRD_PARTY_NOTICES.
#if UNITY_EDITOR
using System;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace FigmaUnityUI
{
    [Serializable] public class BoundsData { public float x, y, width, height; }
    [Serializable] public class AssetEntry
    {
        public string nodeId, figmaName, assetType, fileName, unityPath, format, filterMode;
        public int scaleFactor;
        public BoundsData sourceBounds;
        public bool alphaRequired, nineSlice;
        public float[] border;
    }
    [Serializable] public class AssetManifest
    {
        public int schemaVersion;
        public string figmaFile, rootNodeId;
        public AssetEntry[] assets;
    }

    public static class FigmaUIAssetImporter
    {
        public const string ManifestPath = "Assets/UI/FigmaSync/figma_asset_manifest.json";

        public static string SafeAssetPath(string path)
        {
            if (string.IsNullOrEmpty(path) || !path.StartsWith("Assets/", StringComparison.Ordinal) ||
                path.Contains("\\") || path.Contains(":") || Array.Exists(path.Split('/'), s => s == ".." || s == "." || s == ""))
                throw new ArgumentException("Invalid project asset path: " + path);
            return path;
        }

        public static AssetManifest Read(string path)
        {
            var manifest = JsonUtility.FromJson<AssetManifest>(File.ReadAllText(SafeAssetPath(path)));
            if (manifest == null || manifest.schemaVersion != 1 || manifest.assets == null)
                throw new InvalidDataException("Expected asset manifest schemaVersion 1");
            return manifest;
        }

        [MenuItem("Tools/Figma UI/Import Default Asset Manifest")]
        public static void ImportDefault() { Import(ManifestPath); }

        public static void Import(string manifestPath)
        {
            var manifest = Read(manifestPath);
            // Preflight the entire batch before changing import settings.
            foreach (var a in manifest.assets)
            {
                SafeAssetPath(a.unityPath);
                if (!File.Exists(a.unityPath)) throw new FileNotFoundException(a.unityPath);
                if (a.format != "png") throw new NotSupportedException("SVG requires a project-approved SVG importer or PNG rasterization: " + a.unityPath);
                if (a.scaleFactor < 1 || a.scaleFactor > 4 || a.sourceBounds == null || a.sourceBounds.width <= 0 || a.sourceBounds.height <= 0)
                    throw new InvalidDataException("Invalid size/scale: " + a.unityPath);
                if (a.nineSlice && (a.border == null || a.border.Length != 4 ||
                    Array.Exists(a.border, b => b < 0) || a.border[0]+a.border[2] >= a.sourceBounds.width ||
                    a.border[1]+a.border[3] >= a.sourceBounds.height)) throw new InvalidDataException("Invalid border");
                if (!string.IsNullOrEmpty(a.filterMode) && !Enum.TryParse<FilterMode>(a.filterMode, out _))
                    throw new InvalidDataException("Invalid filterMode");
            }
            AssetDatabase.Refresh();
            foreach (var a in manifest.assets)
            {
                var importer = AssetImporter.GetAtPath(a.unityPath) as TextureImporter;
                if (importer == null) throw new InvalidDataException("Not a texture: " + a.unityPath);
                importer.textureType = TextureImporterType.Sprite;
                importer.spriteImportMode = SpriteImportMode.Single;
                var settings = new TextureImporterSettings();
                importer.ReadTextureSettings(settings);
                settings.spriteMeshType = SpriteMeshType.FullRect;
                importer.SetTextureSettings(settings);
                importer.alphaSource = TextureImporterAlphaSource.FromInput;
                importer.alphaIsTransparency = true;
                importer.wrapMode = TextureWrapMode.Clamp;
                importer.mipmapEnabled = false;
                importer.npotScale = TextureImporterNPOTScale.None;
                importer.filterMode = string.IsNullOrEmpty(a.filterMode) ? FilterMode.Bilinear : (FilterMode)Enum.Parse(typeof(FilterMode), a.filterMode);
                importer.textureCompression = TextureImporterCompression.Uncompressed;
                int width = Mathf.RoundToInt(a.sourceBounds.width * a.scaleFactor);
                int height = Mathf.RoundToInt(a.sourceBounds.height * a.scaleFactor);
                if (Math.Max(width,height) > 16384) throw new InvalidDataException("Texture exceeds 16384 pixels");
                importer.maxTextureSize = Mathf.Clamp(Mathf.NextPowerOfTwo(Math.Max(width,height)),32,16384);
                // With Canvas.referencePixelsPerUnit=100, native size remains design size.
                importer.spritePixelsPerUnit = 100 * a.scaleFactor;
                importer.spriteBorder = a.nineSlice ? new Vector4(a.border[0],a.border[1],a.border[2],a.border[3]) * a.scaleFactor : Vector4.zero;
                importer.SaveAndReimport();
                var sprite = AssetDatabase.LoadAssetAtPath<Sprite>(a.unityPath);
                if (sprite == null || sprite.rect.width != width || sprite.rect.height != height)
                    throw new InvalidDataException("Sprite size mismatch (check platform overrides): " + a.unityPath);
            }
            Debug.Log("Figma UI: imported " + manifest.assets.Length + " sprites");
        }
    }
}
#endif
