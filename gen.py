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
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    return name.strip('-')

def prepare_public_directory():
    if os.path.exists('public'):
        shutil.rmtree('public')
    os.makedirs('public')

def process_markdown_files():
    import frontmatter
    import markdown
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound

    env = Environment(loader=FileSystemLoader('.'))

    md_files = glob('*.md')
    if not md_files:
        print("⚠️ No Markdown files found in the root directory")
        return []

    processed = []

    for path in md_files:
        try:
            post = frontmatter.load(path)
            base = os.path.splitext(os.path.basename(path))[0]

            if base == 'index':
                output_path = os.path.join('public', 'index.html')
                permalink = '/'
            else:
                slug = clean_filename(base)
                os.makedirs(os.path.join('public', slug), exist_ok=True)
                output_path = os.path.join('public', slug, 'index.html')
                permalink = f'/{slug}/'

            context = {
                'title': post.get('title', 'Untitled'),
                'desc': post.get('desc', ''),
                'image': post.get('image', ''),
                'content': markdown.markdown(post.content),
                'permalink': permalink,
                'original_path': path
            }

            template_name = post.get('template', 'default.html')
            try:
                template = env.get_template(template_name)
            except TemplateNotFound:
                print(f"❌ Template '{template_name}' not found in root")
                continue

            html = template.render(context)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

            processed.append({'input': path, 'output': output_path, 'permalink': permalink})
            print(f"✅ Rendered: {path} → {output_path}")

        except Exception as e:
            print(f"❌ Error processing {path}: {e}")

    return processed

def main():
    check_and_install_packages()
    prepare_public_directory()
    pages = process_markdown_files()
    if pages:
        print("\n📄 Rendering complete:")
        for page in pages:
            print(f"• {page['input']} → {page['output']} (URL: {page['permalink']})")

if __name__ == "__main__":
    main()
