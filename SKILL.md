---
name: figma-unity-ui
description: 严格按 UI 效果图、Figma 设计稿或节点还原 Unity UGUI，保留原始 UI 外观，生成透明 PNG/SVG、Manifest、Sprite 设置、9-Slice 和 Prefab/Screen，并执行 Alpha 与整屏/局部视觉验收。用于 Figma 切图、Unity UI 还原和同步；面向 Unity 2022.3 LTS、Unity 6、TextMeshPro。
---

# Figma → Unity UI

## 严格还原合同（默认）

用户给出的效果图／Figma 是视觉真值，默认目标是完全一致，而非重新设计。执行前必读 [视觉还原与验收](references/visual-fidelity.md)。不得自行替换图标、Logo、字体、背景、插画、渐变、阴影、圆角、布局、图表分段或状态样式；“简单形状用原生 UI”只决定实现方式，不授权改变外观。演示生成器和基础 Prefab 不是用户设计素材。

先保存不可变参考图与逐元素来源、测量、实现方法及未解决差异记录。能从原节点导出的就导出原节点；截图缺失细节时忠实重建并对照验证，不用通用图标或 AI 重绘冒充原素材。只有用户明确授权的设计变更才可替换，记录授权原文。无法可靠还原的部分保持未通过，继续完成不受影响的区域；必要时请求缺失原始素材，禁止悄悄降低目标。

技术通过、Alpha 通过、视觉通过分别报告。完成必须有真实 Unity 渲染与同尺寸参考图的整屏及局部对照、黑白／棋盘背景检查和逐项视觉结论。`compare_images.py --exact` 检查像素完全一致；非零差异不能称为像素一致。抗锯齿等容差只能按预先记录的验收合同使用，不能为消除失败而提高阈值、模糊、拉伸或删掉失败区域。截图无法保证恢复原始图层、字体及被遮挡像素，必须如实说明，不能承诺工具必然实现零差异。

## 工作边界

先读当前输入和 Unity 项目规范。以当前 Figma Root Frame 尺寸为设计坐标系，映射到 `CanvasScaler.referenceResolution`；截图输入使用其原始尺寸并记录测量不确定性。不要把整屏截图作为最终 Screen。

脚本和 references 相对于**本 SKILL.md 所在目录**解析；从其他项目调用时使用它们的绝对路径。项目资源路径则相对于明确的 Unity 项目根目录。先安装 `requirements.txt`，不要因缺依赖跳过 QA。

## 执行流程

1. **理解结构**：有 Figma MCP 时先读真实节点、组件、实例、Auto Layout、文字、向量、图片、蒙版、变量及 Export Settings，再用截图核对视觉。读 [Figma 工作流](references/figma-workflow.md)。仅使用当前可用工具，遵守所用 Figma/Unity 集成的技能前置要求；不猜工具名称。
2. **分类**：Text → `TextMeshProUGUI`；简单形状 → Figma 原生形状或 Unity 原生 UI／可复用形状 Sprite；简单图标 → 源 Vector/SVG，必要时高分辨率 PNG；复杂纹理／插画／发光 → PNG；重复元素 → Prefab；3D 区 → Viewport。禁止文字烘焙进素材。UGUI Image 本身不能任意画圆角，选择实际支持的形状组件或共享 9-slice Sprite。
3. **建合同**：先写 `figma_asset_manifest.json` 和 `figma_ui_manifest.json`。读 [Manifest](references/manifest-schema.md)，参考 [资产示例](examples/figma_asset_manifest.example.json) 和 [结构示例](examples/figma_ui_manifest.example.json)。`export/*` 是独立导出节点，转换为英文 lowercase snake_case。不要机械转换所有 Frame。
4. **BBox 与导出**：读 [切图](references/slicing.md)。生成 BBox preview 后核对完整阴影、透明留白和相邻文字。默认 2x，低于 64 设计单位的图标优先 3x/4x 原生导出。倍率只增加像素，不增加 RectTransform 尺寸。禁止自动 Trim。
5. **强制透明验收**：读 [Alpha 质量](references/alpha-quality.md)。透明 circle、rounded、capsule、irregular、icon、badge、decoration 必须运行 Alpha Audit，并实际查看黑底、白底和棋盘格。文件写入、脚本退出码 0、`PASS` 均不等于视觉验收通过。`REVIEW` 色边提示必须检查并记录结论；存在底色、裁切或错误边缘时重出。不能把 `alphaRequired` 改 false 来通过检查。
6. **Unity 导入**：读 [Unity Import](references/unity-import.md)；优先项目规范，否则用 `Assets/UI`。校验 Manifest 和文件，再通过 Unity MCP／Editor 执行导入器。[9-slice](references/nine-slice.md) 的 border 以设计单位记录，导入时乘导出倍率。
7. **组件与 Screen**：读 [Prefab 工作流](references/unity-prefabs.md)。优先 Unity MCP 或附带 Editor 构建器；不手写 `.prefab` YAML。按钮根挂 Button，子级 Background／Icon／Label，Label 为 TMP。简单状态用 ColorTint，明显形态变化用 SpriteState。保留项目已有交互和组件逻辑。
8. **Unity QA**：检查 Sprite、Alpha、方形底、Missing Sprite／Font／Script、Prefab 引用、语义层级、可编辑 TMP、可交互 Button、9-slice、至少两种宽高比及 Console Error。必须按视觉还原参考执行整屏和局部比较，不能用节点数量或编译通过代替视觉验收。无真实渲染、灰屏／空白捕获或有未解决差异时视觉未通过。没有 Editor 时交付资源和脚本，明确运行验证未执行，不声称已创建或验证 Prefab。

## 常用命令

下列命令在本技能目录执行；`test-output/demo` 为隔离示例目录，不是现有项目。

```bash
python scripts/create_example_assets.py --project-root test-output/demo
python scripts/validate_manifest.py test-output/demo/Assets/UI/FigmaSync/figma_asset_manifest.json --project-root test-output/demo
python scripts/validate_manifest.py test-output/demo/Assets/UI/FigmaSync/figma_ui_manifest.json --assets test-output/demo/Assets/UI/FigmaSync/figma_asset_manifest.json
python scripts/audit_png_assets.py --manifest test-output/demo/Assets/UI/FigmaSync/figma_asset_manifest.json --project-root test-output/demo --qa-dir test-output/qa --report test-output/alpha_report.json
```

## MCP 缺失时

Figma MCP 不可用：使用用户提供的节点导出／源图，记录缺失的节点元数据；不宣称同步远端。Unity MCP 不可用但 Editor 可用：执行附带 Editor 脚本。两者都不可用仍完成本地可运行产物和 QA，列出实际缺失的连接／编辑器验证。不要因普通技术选择反复确认；覆盖已有手工编辑 Prefab 前先审查差异并遵循用户授权范围。

## 交付

提供素材、两个 Manifest、QA 图片与报告、导入／Prefab 路径和验证状态，同时交付 `visual_fidelity_report.json`（来源、锁定阈值、区域、授权变更、逐项审查、剩余差异）。技术通过但视觉未通过只能交付“结构初稿／待视觉修正”。Figma 额度不足不授权简化视觉，空远程文件不算 Figma 重建完成。明确源图低清、SVG 支持、未连接 Viewport 或未绑定业务事件等实际限制。

## 触发示例

- 使用 $figma-unity-ui 将当前 Figma 页面切分成 Unity UGUI 可用素材，导出透明 PNG，并直接同步到我的 Unity 项目。
- 使用 $figma-unity-ui 检查这些圆形 UI 切图，清理背景残留并执行 Alpha QA。
- 使用 $figma-unity-ui 根据当前 Figma Frame 在 Unity 中创建 Prefab 和 Screen Hierarchy。
