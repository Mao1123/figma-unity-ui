// Copy into an isolated project's Editor folder; invoke FigmaUnityUISmoke.Run.
#if UNITY_EDITOR
using System;
using System.IO;
using FigmaUnityUI;
using TMPro;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

public static class FigmaUnityUISmoke
{
    static void Require(bool value,string message) { if(!value) throw new Exception(message); }
    public static void Run()
    {
        const string fontPath="Assets/TextMesh Pro/Resources/Fonts & Materials/LiberationSans SDF.asset";
        if(AssetDatabase.LoadAssetAtPath<TMP_FontAsset>(fontPath)!=null) { Execute(); return; }
        AssetDatabase.importPackageCompleted += OnImported;
        AssetDatabase.importPackageFailed += OnFailed;
        var package=UnityEditor.PackageManager.PackageInfo.FindForAssembly(typeof(TMP_Text).Assembly);
        AssetDatabase.ImportPackage(Path.Combine(package.resolvedPath,"Package Resources/TMP Essential Resources.unitypackage"),false);
    }
    static void OnImported(string name)
    {
        AssetDatabase.importPackageCompleted -= OnImported;
        AssetDatabase.importPackageFailed -= OnFailed;
        EditorApplication.delayCall += Execute;
    }
    static void OnFailed(string name,string error) { Debug.LogError(error); EditorApplication.Exit(1); }
    static void Execute()
    {
        try
        {
            AssetDatabase.Refresh();
            string uiPath=FigmaUIPrefabBuilder.UIPath;
            var manifest=JsonUtility.FromJson<UIManifest>(File.ReadAllText(uiPath));
            manifest.fontAsset="Assets/TextMesh Pro/Resources/Fonts & Materials/LiberationSans SDF.asset";
            File.WriteAllText(uiPath,JsonUtility.ToJson(manifest,true));
            FigmaUIAssetImporter.ImportDefault();
            var icon=AssetDatabase.LoadAssetAtPath<Sprite>("Assets/UI/Icons/icon_back.png");
            Require(icon!=null && icon.rect.width==96 && icon.pixelsPerUnit==300,"Icon density failed");
            var panel=AssetDatabase.LoadAssetAtPath<Sprite>("Assets/UI/Panels/panel_information.png");
            Require(panel!=null && panel.border==new Vector4(40,40,40,40),"9-slice border failed");
            FigmaUIPrefabBuilder.BuildDefault();
            var screen=AssetDatabase.LoadAssetAtPath<GameObject>(manifest.unityPrefab);
            Require(screen!=null,"Missing Screen prefab");
            Require(screen.GetComponentsInChildren<Button>(true).Length==6,"Expected six buttons");
            Require(screen.GetComponentsInChildren<TextMeshProUGUI>(true).Length==8,"Expected eight editable TMP texts");
            Require(screen.transform.Find("Content/InformationPanel").GetComponent<Image>().type==Image.Type.Sliced,"Image not sliced");
            Require(PrefabUtility.GetCorrespondingObjectFromSource(screen.transform.Find("Header/Btn_Back").gameObject)!=null,"Nested prefab source missing");
            foreach(var t in screen.GetComponentsInChildren<Transform>(true)) Require(GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject)==0,"Missing script");
            Selection.activeGameObject=screen; FigmaUIValidator.ValidateSelected();
            File.WriteAllText("smoke-result.json","{\"passed\":true,\"unityVersion\":\""+Application.unityVersion+"\",\"buttons\":6,\"texts\":8}");
            Debug.Log("FIGMA_UNITY_SMOKE_PASS");
            EditorApplication.Exit(0);
        }
        catch(Exception e) { Debug.LogException(e); EditorApplication.Exit(1); }
    }
}
#endif
