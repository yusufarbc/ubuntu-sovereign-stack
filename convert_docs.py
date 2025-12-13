import os
import re

# Configuration
SOURCE_DIR = 'docs'
TARGET_DIR = 'website/docs'

# Ensure target directory exists
os.makedirs(TARGET_DIR, exist_ok=True)

# Base Template (Broken into parts to inject Active class dynamically)
TEMPLATE_HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Ubuntu Sovereign Stack</title>
    <link rel="stylesheet" href="../assets/css/style.css">
    <style>
        /* Local overrides for docs readability */
        body {{
            background-color: #f7f9fc;
        }}
    </style>
</head>
<body>

    <!-- Global Navigation -->
    <nav class="navbar">
        <div class="nav-container">
            <a href="../index.html" class="brand">Ubuntu Sovereign Stack</a>
            <ul class="nav-links">
                <li><a href="../index.html" class="nav-link">Home</a></li>
                <li><a href="project_proposal.html" class="nav-link {active_proposal}">Proposal</a></li>
                <li><a href="vision.html" class="nav-link {active_vision}">Vision</a></li>
                <li><a href="architecture.html" class="nav-link {active_architecture}">Architecture</a></li>
                <li><a href="index.html" class="nav-link {active_docs}">Docs</a></li>
            </ul>
            <a href="https://github.com/yusufarbc/ubuntu-sovereign-stack" class="btn-github" target="_blank">
                GitHub &rarr;
            </a>
        </div>
    </nav>

    <div class="container">
        <div class="docs-content">
            {back_link}
            {content}
        </div>
    </div>

    <footer>
        <p>Ubuntu Sovereign Stack &copy; 2025. Project Documentation.</p>
    </footer>

</body>
</html>
"""

def parse_markdown(text):
    # Escape HTML
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    lines = text.split('\n')
    html_lines = []
    in_list = False
    in_code_block = False
    in_table = False

    for line in lines:
        stripped_line = line.strip()

        # Code Block
        if stripped_line.startswith('```'):
            if in_code_block:
                html_lines.append('</pre>')
                in_code_block = False
            else:
                html_lines.append('<pre>')
                in_code_block = True
            continue
        
        if in_code_block:
            html_lines.append(line)
            continue

        # Table State Machine
        if stripped_line.startswith('|'):
            if not in_table:
                html_lines.append('<table>')
                in_table = True
                # Assume first row is header
                html_lines.append('<thead><tr>')
                cells = [c.strip() for c in stripped_line.strip('|').split('|')]
                for cell in cells:
                    html_lines.append(f'<th>{parse_inline(cell)}</th>')
                html_lines.append('</tr></thead><tbody>')
                continue
            else:
                # Check for separator row (e.g., |---|---|)
                if '---' in stripped_line:
                    continue
                # Body row
                html_lines.append('<tr>')
                cells = [c.strip() for c in stripped_line.strip('|').split('|')]
                for cell in cells:
                    html_lines.append(f'<td>{parse_inline(cell)}</td>')
                html_lines.append('</tr>')
                continue
        else:
            if in_table:
                html_lines.append('</tbody></table>')
                in_table = False

        # Headlines (with ID generation for linking if needed, simple version)
        if line.startswith('# '):
            html_lines.append(f'<h1>{line[2:]}</h1>')
            continue
        if line.startswith('## '):
            html_lines.append(f'<h2>{line[3:]}</h2>')
            continue
        if line.startswith('### '):
            html_lines.append(f'<h3>{line[4:]}</h3>')
            continue

        # Blockquotes
        if line.startswith('> '):
            content = line[2:]
            html_lines.append(f'<blockquote>{parse_inline(content)}</blockquote>')
            continue

        # Lists
        if line.strip().startswith('* ') or line.strip().startswith('- '):
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            content = line.strip()[2:]
            html_lines.append(f'<li>{parse_inline(content)}</li>')
            continue
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False

        # Empty lines
        if not line.strip():
            continue

        # Paragraphs (fallback)
        html_lines.append(f'<p>{parse_inline(line)}</p>')

    if in_list:
        html_lines.append('</ul>')
    if in_table:
        html_lines.append('</tbody></table>')

    return '\n'.join(html_lines)

def parse_inline(text):
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Links: [Text](URL)
    def link_replacer(match):
        label = match.group(1)
        url = match.group(2)
        if url.endswith('.md'):
            url = url.replace('.md', '.html')
        # Remove docs/ prefix if linking to sibling files from within docs/
        url = url.replace('docs/', '') 
        return f'<a href="{url}">{label}</a>'
    
    text = re.sub(r'\[(.*?)\]\((.*?)\)', link_replacer, text)
    
    # Backticks for inline code
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    
    return text

def main():
    for filename in os.listdir(SOURCE_DIR):
        if filename.endswith('.md'):
            source_path = os.path.join(SOURCE_DIR, filename)
            target_filename = filename.replace('.md', '.html').lower()
            target_path = os.path.join(TARGET_DIR, target_filename)

            with open(source_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            title = filename.replace('.md', '').replace('_', ' ').title()
            
            # Determine Active Link
            active_proposal = 'active' if 'proposal' in target_filename else ''
            active_vision = 'active' if 'vision' in target_filename else ''
            active_architecture = 'active' if 'architecture' in target_filename else ''
            
            # If none of the specific ones, fallback to "Docs" for other pages
            active_docs = ''
            if not (active_proposal or active_vision or active_architecture):
                active_docs = 'active'

            # Logic for "Back to Index" link
            # We don't want to show "Back to Index" if we are ALREADY on the index page
            if target_filename == 'index.html':
                 back_link_html = ''
            else:
                 back_link_html = '<a href="index.html" class="nav-link" style="display:inline-block; margin-bottom:1rem; color:var(--primary); padding:0;">&larr; Back to Index</a>'

            html_content = parse_markdown(md_content)
            
            full_html = TEMPLATE_HEADER.format(
                title=title, 
                content=html_content,
                active_proposal=active_proposal,
                active_vision=active_vision,
                active_architecture=active_architecture,
                active_docs=active_docs,
                back_link=back_link_html
            )

            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            print(f'Converted {filename} -> {target_filename}')

if __name__ == "__main__":
    main()
