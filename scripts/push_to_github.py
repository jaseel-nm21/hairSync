"""
HairSync GitHub Push Helper
Allows pushing to GitHub directly or using standard git.
Usage:
    python scripts/push_to_github.py <github_repo_url>
Example:
    python scripts/push_to_github.py https://github.com/yourusername/HairSync.git
"""

import sys
import os
from dulwich import porcelain
from dulwich.repo import Repo

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/push_to_github.py <remote_url>")
        print("Example: python scripts/push_to_github.py https://github.com/username/HairSync.git")
        sys.exit(1)

    remote_url = sys.argv[1].strip()
    repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    print(f"Connecting to remote: {remote_url}...")
    try:
        porcelain.remote_add(repo_path, 'origin', remote_url)
        print("[+] Remote 'origin' added.")
    except Exception:
        print("[*] Remote 'origin' already exists or configured.")

    print("[*] Pushing 'master' branch to GitHub...")
    print("If prompted, enter your GitHub Username and Personal Access Token (PAT):")
    try:
        porcelain.push(repo_path, remote_url, 'refs/heads/master')
        print("[+] Successfully pushed to GitHub!")
    except Exception as e:
        print(f"[-] Push note/error: {e}")
        print("\nAlternatively, if you install Git for Windows, you can run:")
        print(f"  git remote add origin {remote_url}")
        print("  git branch -M main")
        print("  git push -u origin main")
