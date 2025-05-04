import sys
import subprocess
import importlib
import os
import re
from glob import glob
import shutil

def check_and_install_packages():
    required_packages = [
        {'name': 'python-frontmatter', 'import_name': 'frontmatter'},
        {'name': 'markdown', 'import_name': 'markdown'},
        {'name': 'Jinja2', 'import_name': 'jinja2'}
    ]
    
    for package in required_packages:
        try:
            importlib.import_module(package['import_name'])
            print(f"✅ {package['name']} is already installed")
        except ImportError:
            print(f"⚠️ {package['name']} not found. Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package['name']])
                print(f"✅ Successfully installed {package['name']}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package['name']}: {e}")
                sys.exit(1)

def clean_filename(name):
    """Convert to permalink format: lowercase, letters and hyphens only"""
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    name = name.strip('-')
    return name

def prepare_public_directory():
    """Clean and recreate the public directory"""
    if os.path.exists('public'):
        shutil.rmtree('public')
    os.makedirs('public')

def process_markdown_files():
    import frontmatter
    import markdown
    from jinja2 import Environment, FileSystemLoader
    
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('templates'))
    
    # Get all .md files in root directory
    md_files = glob('*.md')
    
    if not md_files:
        print("No Markdown files found in root directory")
        return []
    
    processed_files = []
    
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                post = frontmatter.load(f)
                
                # Determine output path and URL
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                
                if base_name == 'index':
                    output_path = 'public/index.html'
                    permalink = '/'
                else:
                    clean_name = clean_filename(base_name)
                    output_dir = os.path.join('public', clean_name)
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, 'index.html')
                    permalink = f'/{clean_name}/'
                
                # Prepare data for template
                data = {
                    'title': post.get('title', 'Untitled'),
                    'desc': post.get('desc', ''),
                    'template': post.get('template', 'default.html'),
                    'image': post.get('image', ''),
                    'content': markdown.markdown(post.content),
                    'permalink': permalink,
                    'original_path': file_path
                }
                
                # Render with Jinja2
                template = env.get_template(data['template'])
                rendered = template.render(**data)
                
                # Write to file
                with open(output_path, 'w', encoding='utf-8') as out_file:
                    out_file.write(rendered)
                
                processed_files.append({
                    'input': file_path,
                    'output': output_path,
                    'permalink': permalink
                })
                
                print(f"Rendered: {file_path} → {output_path}")
                
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                continue
    
    return processed_files

def main():
    check_and_install_packages()
    prepare_public_directory()
    
    # Process all markdown files
    pages = process_markdown_files()
    
    # Print summary
    print("\nRendering complete:")
    for page in pages:
        print(f"{page['input']} → {page['output']} (URL: {page['permalink']})")

if __name__ == "__main__":
    main()
