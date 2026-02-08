import os
import sys
import shutil
import subprocess

# Add scripts folder to path to import doc_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))
try:
    from doc_utils import init_docs_structure
except ImportError:
    print("Could not import doc_utils. Make sure scripts/doc_utils.py exists.")
    sys.exit(1)

def build_docs():
    # 1. Initialize structure (zh/en folders and _toc.yml)
    init_docs_structure()
    
    base_dir = os.path.dirname(os.path.abspath(__file__)) # docs/
    build_dir = os.path.join(base_dir, '_build', 'html')
    
    # Clean build dir
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir, exist_ok=True)

    # 2. Build Chinese docs
    print("Building Chinese documentation...")
    subprocess.check_call([
        sys.executable, '-m', 'sphinx.cmd.build',
        '-c', base_dir,           # Config directory (docs/)
        '-b', 'html',             # Builder
        '-D', 'language=zh_CN',   # Language override
        os.path.join(base_dir, 'zh'), # Source dir
        os.path.join(build_dir, 'zh') # Output dir
    ])
    
    # 3. Build English docs
    print("Building English documentation...")
    subprocess.check_call([
        sys.executable, '-m', 'sphinx.cmd.build',
        '-c', base_dir,
        '-b', 'html',
        '-D', 'language=en',
        os.path.join(base_dir, 'en'),
        os.path.join(build_dir, 'en')
    ])
    
    # 4. Create root redirect
    redirect_html = """
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0; url=./zh/index.html" />
  </head>
  <body>
    <p>Redirecting to <a href="./zh/index.html">Chinese documentation</a>...</p>
  </body>
</html>
    """
    with open(os.path.join(build_dir, 'index.html'), 'w') as f:
        f.write(redirect_html)
        
    print(f"Build complete. Open {os.path.join(build_dir, 'index.html')} to view.")

if __name__ == '__main__':
    build_docs()
