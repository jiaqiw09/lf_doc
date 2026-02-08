import os
import re
import shutil
import yaml

def parse_summary(summary_path):
    """
    Parses GitBook SUMMARY.md and returns a structure for sphinx-external-toc.
    """
    if not os.path.exists(summary_path):
        return None

    with open(summary_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    root_file = None
    toc_structure = {'root': None, 'subtrees': []}
    
    current_subtree = {'entries': []} # Default bucket (no caption)
    # If we find a caption, we create a new subtree dictionary and append it to toc_structure['subtrees']
    # But wait, sphinx-external-toc format:
    # root: docname
    # subtrees:
    #   - caption: ...
    #     entries: ...
    #   - entries: ... (anonymous group)

    # Let's use a simpler approach: build a list of top-level items, some are files, some are sections.
    
    # We need to track indentation to handle nesting.
    # Stack will store references to the 'entries' list of the current parent.
    # Level 0 is the top-level 'entries' list (inside a caption group or default group).
    
    stack = [] 
    
    # First pass: clean lines and identify sections
    # GitBook format:
    # # Table of contents
    # * [Title](link)
    #   * [Sub](link)
    # ## Caption
    # * [Title](link)
    
    # We will build a list of "sections". Each section has a caption (optional) and a tree of entries.
    sections = []
    current_section = {'caption': None, 'entries': []}
    sections.append(current_section)
    
    # Stack for nesting: (indent_level, entries_list)
    # Initial stack points to the current section's entries
    stack = [(0, current_section['entries'])]
    
    for line in lines:
        line = line.rstrip()
        if not line:
            continue
            
        if line.startswith('# Table of contents'):
            continue
            
        # Check for Section Header (## )
        if line.startswith('## '):
            caption = line.strip('# ').strip()
            current_section = {'caption': caption, 'entries': []}
            sections.append(current_section)
            stack = [(0, current_section['entries'])] # Reset stack for new section
            continue
            
        # Check for List Item
        # Regex to capture indent, title, link
        match = re.match(r'^(\s*)\* \[(.*?)\]\((.*?)\)', line)
        if match:
            indent_str = match.group(1)
            title = match.group(2)
            link = match.group(3)
            
            # Normalize link: remove .md extension, fix paths
            file_path = link
            if file_path.endswith('.md'):
                file_path = file_path[:-3]
            if file_path.startswith('./'):
                file_path = file_path[2:]
            
            # Handle README -> index if it's the root, but GitBook usually links explicitly.
            # In Sphinx, 'README' is just a file.
            
            # Set root if not set
            if not toc_structure['root']:
                toc_structure['root'] = file_path
                continue # Skip adding root to the tree if it's the main landing page?
                # Usually GitBook puts "README.md" as the first item.
                # sphinx-external-toc requires 'root' key.
            
            # If this file is SAME as root, skip adding to entries (to avoid recursion/duplication)
            if file_path == toc_structure['root']:
                continue

            indent_level = len(indent_str)
            
            # Adjust stack based on indentation
            # We look for the last item in stack with indentation < current
            while len(stack) > 1 and stack[-1][0] >= indent_level:
                stack.pop()
                
            parent_entries = stack[-1][1]
            
            # Create new entry
            new_entry = {'file': file_path, 'title': title}
            parent_entries.append(new_entry)
            
            # Push this entry as a potential parent for next items (if they are indented more)
            # The 'subtrees' key is where children go. 
            # But wait, sphinx-external-toc uses 'subtrees' for children?
            # A file entry can have 'subtrees'.
            # "entries: - file: ... subtrees: - entries: ..."
            
            # We need to prepare the 'subtrees' list for this entry just in case
            # But we only add it if children appear.
            # So we push (indent_level, new_entry) to stack?
            # No, we need to push the *list* where children should be added.
            # But we don't know yet if we need 'subtrees'.
            # We can lazily add 'subtrees'.
            
            # Let's just push the entry object itself, and handle 'subtrees' creation when needed.
            stack.append((indent_level, new_entry))
            
        else:
            # Handle nested items that are pushed to the stack but are actually just previous items
            pass

    # Now we need to post-process the stack/entries to ensure correct structure for subtrees
    # My stack logic above was slightly flawed because I pushed `new_entry` but children need to go into `new_entry['subtrees'][0]['entries']`?
    # Let's refine the stack logic.
    pass

def convert_summary_to_toc(summary_path, output_path):
    # Re-implementing with a cleaner recursive or iterative approach
    if not os.path.exists(summary_path):
        print(f"Summary file not found: {summary_path}")
        return

    with open(summary_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    toc = {'root': None, 'subtrees': []}
    
    # Current active list to append items to.
    # Initially, we append to a default subtree in the main toc.
    # But wait, we have sections.
    
    sections = [] # List of {caption: ..., entries: []}
    current_section_entries = []
    current_caption = None
    
    # We will store items in a flat list per section first, then restructure? 
    # No, indentation matters immediately.
    
    # Stack: list of (indent_level, container_list)
    # Container list is where we append new items.
    stack = [(0, current_section_entries)]
    
    first_item_is_root = True
    
    for line in lines:
        line = line.rstrip()
        if not line or line.startswith('# Table of contents'):
            continue
            
        if line.startswith('## '):
            # Save current section
            if current_section_entries:
                # If we had a previous section, save it.
                # If current_caption is None, it's the top default section.
                # Only save if not empty
                sections.append({'caption': current_caption, 'entries': current_section_entries})
            
            # Start new section
            current_caption = line.strip('# ').strip()
            current_section_entries = []
            stack = [(0, current_section_entries)]
            continue
            
        match = re.match(r'^(\s*)\* \[(.*?)\]\((.*?)\)', line)
        if match:
            indent = len(match.group(1))
            title = match.group(2)
            path = match.group(3)
            
            if path.endswith('.md'): path = path[:-3]
            if path.startswith('./'): path = path[2:]
            
            if first_item_is_root:
                toc['root'] = path
                first_item_is_root = False
                continue
                
            # Logic to find correct parent in stack
            # Pop stack until we find a parent with strictly less indent
            while len(stack) > 1 and stack[-1][0] >= indent:
                stack.pop()
                
            # Current parent list
            parent_list = stack[-1][1]
            
            # If indent > parent_indent, it means this item is a child of the LAST item in parent_list
            # But wait, the stack logic ensures we are at the right level?
            # If stack top indent == 0 and current indent == 2:
            # We need to find the last item of stack top, and add child to it.
            
            # Let's adjust:
            # If current indent > stack top indent:
            # This implies we need to go deeper into the last item added.
            if indent > stack[-1][0]:
                if not parent_list:
                    # Weird case: indented but no parent? Just add to current.
                    pass
                else:
                    last_item = parent_list[-1]
                    # Ensure last_item has subtrees
                    if 'subtrees' not in last_item:
                        last_item['subtrees'] = [{'entries': []}]
                    
                    # New container is that entries list
                    new_container = last_item['subtrees'][0]['entries']
                    stack.append((indent, new_container))
                    parent_list = new_container

            # Now append the new item
            new_item = {'file': path, 'title': title}
            parent_list.append(new_item)
            
    # Append the final section
    if current_section_entries:
        sections.append({'caption': current_caption, 'entries': current_section_entries})

    # Filter out empty sections
    # And add to toc['subtrees']
    for sec in sections:
        if not sec['entries']:
            continue
        subtree = {'entries': sec['entries']}
        if sec['caption']:
            subtree['caption'] = sec['caption']
        toc['subtrees'].append(subtree)
        
    # Write YAML
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(toc, f, sort_keys=False, allow_unicode=True)
    
    print(f"Generated {output_path}")

def init_docs_structure():
    """
    Initializes docs structure.
    Checks if docs/zh exists.
    """
    base = 'docs'
    zh = os.path.join(base, 'zh')
    en = os.path.join(base, 'en')
    
    # Ensure zh exists
    if not os.path.exists(zh):
        print(f"Error: {zh} source not found. Please ensure docs/zh exists.")
        return

    # Convert SUMMARY.md to _toc.yml for both
    for lang in ['zh', 'en']:
        lang_dir = os.path.join(base, lang)
        summary = os.path.join(lang_dir, 'SUMMARY.md')
        toc = os.path.join(lang_dir, '_toc.yml')
        
        # Create shim README.rst if README.md exists to satisfy Sphinx default master_doc preference
        # or just to ensure it works.
        readme_md = os.path.join(lang_dir, 'README.md')
        readme_rst = os.path.join(lang_dir, 'README.rst')
        if os.path.exists(readme_md) and not os.path.exists(readme_rst):
            with open(readme_rst, 'w', encoding='utf-8') as f:
                f.write(".. include:: README.md\n   :parser: myst_parser.sphinx_\n")

        if os.path.exists(summary):
            convert_summary_to_toc(summary, toc)

if __name__ == '__main__':
    init_docs_structure()
