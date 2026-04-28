# Obsidian to Anki Converter

将 Obsidian 中的 Markdown 文本（包含 LaTeX 公式）转换为 Anki 可用的 HTML 格式。

## 功能特性

- ✅ **Markdown 基本语法支持**
  - 标题（H1-H6）
  - 粗体、斜体、删除线、高亮
  - 无序列表和有序列表
  - 引用块
  - 段落

- ✅ **LaTeX 数学公式**
  - 行内公式：`$...$`
  - 块级公式：`$$...$$`
  - 自动转换为 Anki MathJax 格式

- ✅ **代码支持**
  - 代码块（带语言标识）
  - 行内代码

- ✅ **链接和图片**
  - Obsidian 内部链接 `[[...]]`
  - Markdown 链接 `[text](url)`
  - Obsidian 内部图片 `![[...]]`
  - Markdown 图片 `![alt](url)`

## 安装依赖

```bash
pip install pyperclip
```

## 使用方法

### 交互模式（推荐）

运行脚本后，每次按回车键会自动读取剪贴板中的 Markdown 内容并转换：

```bash
python obsidian_to_anki.py
```

**使用流程：**
1. 在 Obsidian 中复制包含 Markdown 格式的文本
2. 在终端中按回车键
3. 转换后的 HTML 会自动复制到剪贴板
4. 在 Anki 卡片编辑器中粘贴即可

### 示例

**输入（Markdown）：**
```markdown
# 物理学公式

爱因斯坦的质能方程：$E = mc^2$

## 牛顿第二定律

$$F = ma$$

**重要**：这是经典力学的基础公式。

- 力 F 的单位是牛顿
- 质量 m 的单位是千克
- 加速度 a 的单位是 m/s²
```

**输出（HTML）：**
```html
<h1>物理学公式</h1>
<p>爱因斯坦的质能方程：<anki-mathjax>E = mc^2</anki-mathjax></p>
<h2>牛顿第二定律</h2>
<anki-mathjax>F = ma</anki-mathjax>
<p><b>重要</b>：这是经典力学的基础公式。</p>
<ul>
<li>力 F 的单位是牛顿</li>
<li>质量 m 的单位是千克</li>
<li>加速度 a 的单位是 m/s²</li>
</ul>
```

## 支持的语法对照表

| Markdown 语法 | 转换结果 |
|--------------|---------|
| `# 标题` | `<h1>标题</h1>` |
| `**粗体**` | `<b>粗体</b>` |
| `*斜体*` | `<i>斜体</i>` |
| `~~删除线~~` | `<s>删除线</s>` |
| `==高亮==` | `<mark>高亮</mark>` |
| `$E=mc^2$` | `<anki-mathjax>E=mc^2</anki-mathjax>` |
| `` `代码` `` | `<code>代码</code>` |
| `- 列表项` | `<ul><li>列表项</li></ul>` |
| `1. 列表项` | `<ol><li>列表项</li></ol>` |
| `> 引用` | `<blockquote>引用</blockquote>` |
| `[[链接]]` | `<a href="链接">链接</a>` |
| `![[图片]]` | `<img src="图片">` |

## 注意事项

1. **LaTeX 公式**：转换后的公式使用 `<anki-mathjax>` 标签包裹，Anki 需要安装 MathJax 插件才能正确渲染
2. **剪贴板权限**：确保终端有访问剪贴板的权限
3. **嵌套列表**：支持有序列表后跟随无序子列表的嵌套结构

## 系统要求

- Python 3.6+
- pyperclip 库

## 许可证

MIT License
