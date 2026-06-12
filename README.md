# KCAP Direct3D Game Localizer

一套面向老式 Windows 同人游戏的 Codex 汉化技能，重点处理使用 **KCAP 资源包、Direct3D 9、ANSI GDI 字形缓存、CP932/CP936 混合编码** 的引擎。

## 能做什么

- 索引、提取和无损重建 KCAP 资源包
- 提取 EXE 固定槽文本并安全写回
- 管理日文原文、中文译文和术语一致性
- 替换内置字体并修复特殊符号乱码
- 翻译 DDS 菜单、卡牌和说明图片
- 修复中文末尾白块、错误换行与人名/称号拆分
- 修复 640x480 游戏被非 4:3 分辨率拉伸的问题
- 排查回放界面、切屏和 Alt+Tab 导致的卡死
- 提取 BGM 并生成最终文件哈希清单

## 核心经验

这类引擎的“文本长度”可能同时代表字节容量、字符数和预先创建的纹理槽数量。译文变短时，简单补 ASCII 空格或提前写入 `NUL` 仍可能生成白色矩形。技能会要求先通过游戏同款 `GetGlyphOutlineA` 路径验证空白字形，再使用与原槽一致的双字节零位图占位。

## 使用

将 `skills/kcap-direct3d-game-localizer` 安装到 Codex skills 目录，然后调用：

```text
Use $kcap-direct3d-game-localizer to inspect and localize this KCAP-based game.
```

详细流程、诊断方法和数据格式位于技能目录的 `references/`。

脚本需要 Python 3.10+。PE 交叉引用工具还需要：

```bash
pip install pefile capstone
```

## 仓库内容

- `SKILL.md`：完整工作流与安全规则
- `scripts/`：KCAP、PE 固定槽和 GDI 检查工具
- `references/`：格式说明、排错指南和交付流程

## 版权说明

本仓库只提供通用工具和技术文档，不包含任何游戏本体、可执行文件、字体、音乐、图片、语音、剧情文本或汉化成品。使用者应确保拥有处理相关游戏资源的合法权利。

## License

MIT
