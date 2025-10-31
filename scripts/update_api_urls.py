"""
Update API URLs in all files to use PythonAnywhere backend
"""
import os
import re

# REPLACE THIS with your actual PythonAnywhere username
PYTHONANYWHERE_USERNAME = "yourusername"  # e.g., "praneetha123"
NEW_API_URL = f"https://{PYTHONANYWHERE_USERNAME}.pythonanywhere.com/api"

# Old URLs to replace
OLD_URLS = [
    "https://markmate-api-vbm1.onrender.com/api",
    "http://localhost:8000/api",
]

def update_file(filepath, old_urls, new_url):
    """Update API URLs in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        for old_url in old_urls:
            content = content.replace(old_url, new_url)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[UPDATED] {filepath}")
            return True
        else:
            print(f"[NO CHANGE] {filepath}")
            return False
    except Exception as e:
        print(f"[ERROR] {filepath}: {e}")
        return False

def main():
    print("=" * 60)
    print("Updating API URLs to PythonAnywhere")
    print(f"New API URL: {NEW_API_URL}")
    print("=" * 60)
    
    # Get project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Files to update
    files_to_update = [
        # Frontend files
        os.path.join(project_root, 'frontend', 'login.html'),
        os.path.join(project_root, 'frontend', 'admin.html'),
        os.path.join(project_root, 'frontend', 'student.html'),
        os.path.join(project_root, 'frontend', 'index.html'),
        os.path.join(project_root, 'frontend', 'predict.html'),
        os.path.join(project_root, 'frontend', 'charts.html'),
        
        # Script files
        os.path.join(project_root, 'scripts', 'register_remote_users.py'),
        os.path.join(project_root, 'scripts', 'train_via_api.py'),
        os.path.join(project_root, 'scripts', 'test_login.py'),
    ]
    
    updated_count = 0
    for filepath in files_to_update:
        if os.path.exists(filepath):
            if update_file(filepath, OLD_URLS, NEW_API_URL):
                updated_count += 1
        else:
            print(f"[NOT FOUND] {filepath}")
    
    print("\n" + "=" * 60)
    print(f"Update complete! {updated_count} files updated.")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Commit and push these changes to GitHub")
    print("2. Wait for GitHub Pages to update (1-2 minutes)")
    print("3. Register users on PythonAnywhere:")
    print("   python register_remote_users.py")
    print("   python train_via_api.py")

if __name__ == "__main__":
    if PYTHONANYWHERE_USERNAME == "yourusername":
        print("\n" + "!" * 60)
        print("ERROR: Please edit this script and set your PythonAnywhere username!")
        print("Open: scripts/update_api_urls.py")
        print("Change: PYTHONANYWHERE_USERNAME = 'yourusername'")
        print("To: PYTHONANYWHERE_USERNAME = 'your_actual_username'")
        print("!" * 60)
    else:
        main()
