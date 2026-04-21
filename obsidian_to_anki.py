#!/usr/bin/env python3
"""
Obsidian Markdown to Anki HTML Converter

将 Obsidian 中复制的 Markdown 文本（包含 LaTeX）转换为 Anki 可用的 HTML 格式。
支持：
- Markdown 基本语法（标题、列表、粗体、斜体等）
- LaTeX 数学公式（行内 $...$ 和块级 $$...$$）
- 代码块
- 链接和图片
- 引用块
"""

import re
import pyperclip


def convert_markdown_to_html(markdown_text: str) -> str:
    """
    将 Markdown 文本转换为 Anki 可用的 HTML 格式
    
    Args:
        markdown_text: Obsidian 中复制的 Markdown 文本
        
    Returns:
        转换后的 HTML 字符串
    """
    html = markdown_text
    
    # 1. 保护 LaTeX 公式（避免被其他规则误处理）- 使用更独特的占位符
    # 先处理块级公式 $$...$$
    latex_blocks = []
    def save_latex_block(match):
        latex_blocks.append(match.group(1))
        return f"§LB{len(latex_blocks) - 1}§"
    
    html = re.sub(r'\$\$(.*?)\$\$', save_latex_block, html, flags=re.DOTALL)
    
    # 处理行内公式 $...$ （需要更精确的匹配，避免匹配到 $$）
    latex_inline = []
    def save_latex_inline(match):
        latex_inline.append(match.group(1))
        return f"§LI{len(latex_inline) - 1}§"
    
    # 使用非贪婪匹配，确保不跨越多行，且正确处理转义字符
    html = re.sub(r'\$(?!\$)([^\n]+?)(?<!\$)\$', save_latex_inline, html)
    
    # 2. 处理代码块 ```...```
    code_blocks = []
    def save_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        code_blocks.append((lang, code))
        return f"§CB{len(code_blocks) - 1}§"
    
    html = re.sub(r'```(\w*)\n(.*?)```', save_code_block, html, flags=re.DOTALL)
    
    # 3. 处理行内代码 `...`
    inline_codes = []
    def save_inline_code(match):
        inline_codes.append(match.group(1))
        return f"§IC{len(inline_codes) - 1}§"
    
    html = re.sub(r'`([^`]+)`', save_inline_code, html)
    
    # 4. 处理图片 ![[...]] 或 ![alt](url)
    html = re.sub(r'!\[\[([^\]]+)\]\]', r'<img src="\1">', html)
    html = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', html)
    
    # 5. 处理链接 [[...]] 或 [text](url)
    html = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'<a href="\1">\2</a>', html)
    html = re.sub(r'\[\[([^\]]+)\]\]', r'<a href="\1">\1</a>', html)
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)
    
    # 6. 处理标题
    html = re.sub(r'^###### (.+)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
    html = re.sub(r'^##### (.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # 7. 处理粗体和斜体
    # 粗体 **text** 或 __text__
    html = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', html)
    html = re.sub(r'__(.+?)__', r'<b>\1</b>', html)
    
    # 斜体 *text* 或 _text_
    html = re.sub(r'\*(.+?)\*', r'<i>\1</i>', html)
    html = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<i>\1</i>', html)
    
    # 删除线 ~~text~~
    html = re.sub(r'~~(.+?)~~', r'<s>\1</s>', html)
    
    # 8. 处理引用块 > ...
    html = re.sub(r'^&gt; (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    # 合并连续的 blockquote
    html = re.sub(r'</blockquote>\n<blockquote>', r'\n', html)
    
    # 9. 处理列表
    # 无序列表
    html = re.sub(r'^[-*+] (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    # 有序列表
    html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # 10. 处理段落（空行分隔的文本）
    lines = html.split('\n')
    processed_lines = []
    in_paragraph = False
    paragraph_content = []
    
    for line in lines:
        stripped = line.strip()
        
        # 如果已经是 HTML 标签行，直接添加
        if re.match(r'^<(h[1-6]|ul|ol|li|blockquote|pre|div|img|a|p)', stripped):
            if in_paragraph and paragraph_content:
                processed_lines.append('<p>' + ' '.join(paragraph_content) + '</p>')
                paragraph_content = []
                in_paragraph = False
            processed_lines.append(line)
        elif stripped == '':
            if in_paragraph and paragraph_content:
                processed_lines.append('<p>' + ' '.join(paragraph_content) + '</p>')
                paragraph_content = []
                in_paragraph = False
            processed_lines.append('')
        else:
            in_paragraph = True
            paragraph_content.append(stripped)
    
    # 处理剩余的段落内容
    if paragraph_content:
        processed_lines.append('<p>' + ' '.join(paragraph_content) + '</p>')
    
    html = '\n'.join(processed_lines)
    
    # 11. 恢复代码块
    for i, (lang, code) in enumerate(code_blocks):
        code_escaped = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        html = html.replace(f'§CB{i}§', f'<pre><code class="language-{lang}">{code_escaped}</code></pre>')
    
    # 12. 恢复行内代码
    for i, code in enumerate(inline_codes):
        code_escaped = code.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        html = html.replace(f'§IC{i}§', f'<code>{code_escaped}</code>')
    
    # 13. 恢复 LaTeX 公式
    # Anki 使用 MathJax，需要特定的格式
    for i, latex in enumerate(latex_blocks):
        html = html.replace(f'§LB{i}§', f'\\[{latex}\\]')
    
    for i, latex in enumerate(latex_inline):
        html = html.replace(f'§LI{i}§', f'\\({latex}\\)')
    
    # 14. 包裹列表项到 <ul> 或 <ol>
    # 检测连续的 <li> 并包裹
    html = re.sub(r'((?:<li>.*?</li>\n?)+)', lambda m: '<ul>\n' + m.group(1) + '</ul>' if not re.search(r'^\d', m.group(1)) else '<ol>\n' + m.group(1) + '</ol>', html)
    
    # 15. 清理多余的空行
    html = re.sub(r'\n{3,}', '\n\n', html)
    
    return html.strip()


def main():
    """主函数：交互模式，每次回车从剪贴板读取并转换"""
    print("请粘贴 Markdown 内容：")
    print("按回车键转换剪贴板中的内容（Ctrl+C 退出）\n")
    
    while True:
        try:
            # 等待用户按回车
            input()
            
            # 直接从剪贴板读取内容（避免 PowerShell 粘贴多行丢失换行的问题）
            try:
                markdown_text = pyperclip.paste()
            except Exception as e:
                print(f"读取剪贴板失败：{e}")
                print("请重试...\n")
                continue
            
            if not markdown_text.strip():
                print("剪贴板为空，请先复制内容。\n")
                continue
            
            # 转换
            html_result = convert_markdown_to_html(markdown_text)
            
            # 复制回剪贴板
            try:
                pyperclip.copy(html_result)
            except Exception as e:
                print(f"写入剪贴板失败：{e}")
                # 备用方案：输出到控制台
                print("\n--- 转换结果 ---")
                print(html_result)
                print("----------------\n")
                continue
            
            # 显示转换结果，让用户知道已完成
            print("\n✓ 已转换并复制到剪贴板：")
            print(html_result)
            print("\n" + "-"*40 + "\n")
            
        except KeyboardInterrupt:
            print("\n已退出。")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()
