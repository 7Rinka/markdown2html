from obsidian_to_anki import convert_markdown_to_html

test_input = r"""1. **倒数关系**：
    - $\sec x = \dfrac{1}{\cos x}$
    - $\csc x = \dfrac{1}{\sin x}$
    - $\cot x = \dfrac{1}{\tan x}$
2. **商数关系**：
    - $\tan x = \dfrac{\sin x}{\cos x}$
    - $\cot x = \dfrac{\cos x}{\sin x}$
3. **平方关系**：
    - $\sin^2 x + \cos^2 x = 1$
    - $1 + \tan^2 x = \sec^2 x$
    - $1 + \cot^2 x = \csc^2 x$"""

expected_output = """<ol>
<li><b>倒数关系</b>：</li>
<ul>
<li><anki-mathjax>\\sec x = \\dfrac{1}{\\cos x}</anki-mathjax></li>
<li><anki-mathjax>\\csc x = \\dfrac{1}{\\sin x}</anki-mathjax></li>
<li><anki-mathjax>\\cot x = \\dfrac{1}{\\tan x}</anki-mathjax></li>
</ul>
<li><b>商数关系</b>：</li>
<ul>
<li><anki-mathjax>\\tan x = \\dfrac{\\sin x}{\\cos x}</anki-mathjax></li>
<li><anki-mathjax>\\cot x = \\dfrac{\\cos x}{\\sin x}</anki-mathjax></li>
</ul>
<li><b>平方关系</b>：</li>
<ul>
<li><anki-mathjax>\\sin^2 x + \\cos^2 x = 1</anki-mathjax></li>
<li><anki-mathjax>1 + \\tan^2 x = \\sec^2 x</anki-mathjax></li>
<li><anki-mathjax>1 + \\cot^2 x = \\csc^2 x</anki-mathjax></li>
</ul>
</ol>"""

result = convert_markdown_to_html(test_input)

print("=== Generated Output ===")
print(result)
print("\n=== Expected Output ===")
print(expected_output)
print("\n=== Match? ===")
print(result.strip() == expected_output.strip())
