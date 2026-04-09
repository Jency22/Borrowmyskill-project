import os
import glob

files = glob.glob(r'c:\django\myproject\core\templates\*.html')
for f in files:
    if f.endswith('chatbot.html'):
        continue
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if "{% include 'chatbot.html' %}" not in content:
        content = content.replace('</body>', "{% include 'chatbot.html' %}\n</body>")
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
