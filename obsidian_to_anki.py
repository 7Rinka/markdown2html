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
import sys


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
        # 使用不会被粗体/斜体匹配的占位符（不含字母数字）
        return f"§LB{len(latex_blocks) - 1}§"
    
    html = re.sub(r'\$\$(.*?)\$\$', save_latex_block, html, flags=re.DOTALL)
    
    # 处理行内公式 $...$
    latex_inline = []
    def save_latex_inline(match):
        latex_inline.append(match.group(1))
        return f"§LI{len(latex_inline) - 1}§"
    
    html = re.sub(r'\$(?!\$)(.+?)(?<!\$)\$', save_latex_inline, html)
    
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
    """主函数：从命令行或标准输入读取 Markdown，输出 HTML"""
    import os
    
    # 检查是否有管道输入或文件重定向
    if not os.isatty(0):
        # 从管道或重定向读取
        markdown_text = sys.stdin.read()
        if not markdown_text.strip():
            print("未输入任何内容，退出。")
            return
        html_result = convert_markdown_to_html(markdown_text)
        print(html_result)
        return
    
    # 交互模式
    print("=" * 60)
    print("Obsidian Markdown 转 Anki HTML 转换器")
    print("=" * 60)
    print("\n使用说明:")
    print("1. 从 Obsidian 复制 Markdown 文本")
    print("2. 粘贴到下方（输入单独一行 '---' 结束）")
    print("3. 复制输出的 HTML 到 Anki")
    print("\n支持：LaTeX 公式 ($...$ 和 $$...$$)、代码块、列表、链接等")
    print("-" * 60)
    
    # 从标准输入读取多行文本
    print("\n请粘贴 Markdown 内容（输入单独一行 '---' 结束）:\n")
    
    lines = []
    
    while True:
        try:
            line = input()
            
            # 检查结束条件
            if line.strip() == '---':
                break
            
            lines.append(line)
        except EOFError:
            break
    
    if not lines:
        print("\n未输入任何内容，退出。")
        return
    
    markdown_text = '\n'.join(lines)
    
    # 转换
    html_result = convert_markdown_to_html(markdown_text)
    
    # 输出结果
    print("\n" + "=" * 60)
    print("转换完成的 HTML（可直接复制到 Anki）:")
    print("=" * 60)
    print(html_result)
    print("=" * 60)
    print("\n提示：在 Anki 卡片模板中确保启用了 MathJax 以支持 LaTeX 公式")
    print("如需保存为文件，可使用：python obsidian_to_anki.py < input.md > output.html")


if __name__ == "__main__":
    main()
