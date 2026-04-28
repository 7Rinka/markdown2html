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

    # 高亮 ==text==
    html = re.sub(r'==(.+?)==', r'<mark>\1</mark>', html)

    # 8. 处理引用块 > ...
    html = re.sub(r'^&gt; (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
    # 合并连续的 blockquote
    html = re.sub(r'</blockquote>\n<blockquote>', r'\n', html)

    # 9. 处理列表
    # 无序列表 - 添加临时标记 ol-marker 用于后续识别（支持前导空白）
    html = re.sub(r'^\s*[-*+] (.+)$', r'<li ol-marker="ul">\1</li>', html, flags=re.MULTILINE)
    # 有序列表 - 添加临时标记 ol-marker 用于后续识别（支持前导空白）
    html = re.sub(r'^\s*\d+\. (.+)$', r'<li ol-marker="ol">\1</li>', html, flags=re.MULTILINE)

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
        html = html.replace(f'§LB{i}§', f'<anki-mathjax>{latex}</anki-mathjax>')

    for i, latex in enumerate(latex_inline):
        html = html.replace(f'§LI{i}§', f'<anki-mathjax>{latex}</anki-mathjax>')

    # 14. 包裹列表项到 <ul> 或 <ol>，并移除临时标记
    # 需要将连续的同类型列表项分组，分别包裹
    # 支持嵌套列表：有序列表项后可以跟随无序列表项作为子列表
    def wrap_lists(text):
        lines = text.split('\n')
        result_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            match = re.match(r'^<li ol-marker="(ul|ol)">(.*)</li>$', line.strip())
            
            if match:
                list_type = match.group(1)
                content = match.group(2)
                
                if list_type == 'ol':
                    # 开始一个有序列表项
                    # 检查后续是否有 ul 项目作为子列表
                    sublist_items = []
                    j = i + 1
                    while j < len(lines):
                        sub_match = re.match(r'^<li ol-marker="ul">(.*)</li>$', lines[j].strip())
                        if sub_match:
                            sublist_items.append(sub_match.group(1))
                            j += 1
                        else:
                            break
                    
                    # 输出 ol 项，如果有子列表则嵌套
                    if sublist_items:
                        result_lines.append(f'<li>{content}</li>')
                        result_lines.append('<ul>')
                        for sub_item in sublist_items:
                            result_lines.append(f'<li>{sub_item}</li>')
                        result_lines.append('</ul>')
                        i = j  # 跳过已处理的子列表项
                        continue
                    else:
                        result_lines.append(f'<li>{content}</li>')
                else:  # ul
                    # 独立的无序列表（不在 ol 之后）
                    ul_items = [content]
                    j = i + 1
                    while j < len(lines):
                        ul_match = re.match(r'^<li ol-marker="ul">(.*)</li>$', lines[j].strip())
                        if ul_match:
                            ul_items.append(ul_match.group(1))
                            j += 1
                        else:
                            break
                    
                    result_lines.append('<ul>')
                    for item in ul_items:
                        result_lines.append(f'<li>{item}</li>')
                    result_lines.append('</ul>')
                    i = j
                    continue
            else:
                result_lines.append(line)
            
            i += 1
        
        # 现在需要将连续的 ol 项包裹到 <ol> 标签中
        final_lines = []
        k = 0
        while k < len(result_lines):
            line = result_lines[k]
            if line.strip().startswith('<li>') and not line.strip().startswith('<li>§'):
                # 收集连续的 ol 项（可能后面跟着 <ul>...</ul>）
                ol_items = []
                has_sublist = False
                while k < len(result_lines):
                    curr = result_lines[k]
                    curr_stripped = curr.strip()
                    
                    if curr_stripped.startswith('<li>') and not curr_stripped.startswith('<li>§'):
                        ol_items.append(curr)
                        k += 1
                        # 检查下一个是否是 <ul>
                        if k < len(result_lines) and result_lines[k].strip() == '<ul>':
                            has_sublist = True
                            # 收集整个 <ul>...</ul> 块
                            ul_block = []
                            while k < len(result_lines):
                                ul_line = result_lines[k]
                                ul_block.append(ul_line)
                                k += 1
                                if ul_line.strip() == '</ul>':
                                    break
                            ol_items.extend(ul_block)
                    elif curr_stripped == '<ul>' or curr_stripped.startswith('<li>§'):
                        # 这是子列表的一部分，应该已经在前面的循环中处理了
                        k += 1
                    else:
                        break
                
                if ol_items:
                    final_lines.append('<ol>')
                    final_lines.extend(ol_items)
                    final_lines.append('</ol>')
                continue
            else:
                final_lines.append(line)
            k += 1
        
        return '\n'.join(final_lines)

    html = wrap_lists(html)

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