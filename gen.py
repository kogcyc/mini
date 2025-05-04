import sys
import subprocess
import importlib

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

def main():
    check_and_install_packages()
    
    # Now safely import the packages
    import frontmatter
    import markdown
    import jinja2
    
    print("\nAll required packages are available:")
    print(f"python-frontmatter version: {frontmatter.__version__}")
    print(f"markdown version: {markdown.version}")
    print(f"Jinja2 version: {jinja2.__version__}")

if __name__ == "__main__":
    main()
