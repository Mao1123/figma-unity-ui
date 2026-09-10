#if UNITY_EDITOR
using System.Text;
using TMPro;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

namespace FigmaUnityUI
{
    public static class FigmaUIValidator
    {
        [MenuItem("Tools/Figma UI/Validate Selected Hierarchy")]
        public static void ValidateSelected()
        {
            if(Selection.activeGameObject==null) { Debug.LogError("Select a screen instance or prefab"); return; }
            int errors=0; var report=new StringBuilder();
            foreach(var t in Selection.activeGameObject.GetComponentsInChildren<Transform>(true))
            {
                int missing=GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject);
                if(missing>0) { errors+=missing; report.AppendLine("Missing Script: "+t.name); }
                if(t.name=="GameObject" || t.name.Contains("(Clone)")) report.AppendLine("Review semantic name: "+t.name);
                foreach(var c in t.GetComponents<Component>())
                {
                    if(c==null) continue;
                    var serialized=new SerializedObject(c); var property=serialized.GetIterator();
                    while(property.NextVisible(true))
                        if(property.propertyType==SerializedPropertyType.ObjectReference && property.objectReferenceValue==null && property.objectReferenceInstanceIDValue!=0)
                        { errors++; report.AppendLine("Broken reference: "+t.name+" / "+property.propertyPath); }
                }
                var image=t.GetComponent<Image>();
                if(image!=null && image.gameObject.activeInHierarchy && image.sprite==null)
                    report.AppendLine("Review Missing Sprite (plain native rectangles may be intentional): "+t.name);
                if(image!=null && image.type==Image.Type.Sliced && (image.sprite==null || image.sprite.border==Vector4.zero))
                { errors++; report.AppendLine("Invalid 9-slice: "+t.name); }
                var text=t.GetComponent<TextMeshProUGUI>();
                if(text!=null && text.font==null) { errors++; report.AppendLine("Missing Font: "+t.name); }
                var button=t.GetComponent<Button>();
                if(button!=null)
                {
                    if(button.targetGraphic==null) { errors++; report.AppendLine("Button targetGraphic missing: "+t.name); }
                    if(!button.interactable) report.AppendLine("Review disabled button: "+t.name);
                    if(button.onClick.GetPersistentEventCount()==0) report.AppendLine("Runtime callback test needed: "+t.name);
                }
            }
            report.AppendLine("Errors: "+errors+". Manual checks remain: alpha backgrounds, clipping, fonts/glyphs, resolution variants, input, prefab sources and Console.");
            if(errors>0) Debug.LogError(report.ToString()); else Debug.Log(report.ToString());
        }
    }
}
#endif
