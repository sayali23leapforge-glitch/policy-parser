#!/usr/bin/env python3
"""
Quick deployment verification script
Checks all necessary files and configurations before deploying to Render
"""

import os
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_file(filepath, description):
    """Check if a file exists"""
    exists = os.path.isfile(filepath)
    status = f"{GREEN}✓{RESET}" if exists else f"{RED}✗{RESET}"
    print(f"{status} {description}: {filepath}")
    return exists

def check_content(filepath, search_string, description):
    """Check if a file contains specific content"""
    if not os.path.isfile(filepath):
        print(f"{RED}✗{RESET} File not found: {filepath}")
        return False
    
    with open(filepath, 'r') as f:
        content = f.read()
        found = search_string in content
        status = f"{GREEN}✓{RESET}" if found else f"{RED}✗{RESET}"
        print(f"{status} {description}")
        return found

def main():
    print(f"\n{BLUE}{'='*60}")
    print("AUTO DASHBOARD - RENDER DEPLOYMENT VERIFICATION")
    print(f"{'='*60}{RESET}\n")
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    all_good = True
    
    # Check required files
    print(f"{YELLOW}[1/4] Checking required files...{RESET}")
    required_files = [
        ('Procfile', 'Procfile - Process file'),
        ('render.yaml', 'render.yaml - Render configuration'),
        ('requirements.txt', 'requirements.txt - Python dependencies'),
        ('runtime.txt', 'runtime.txt - Python version'),
        ('run.py', 'run.py - Entry point'),
        ('.gitignore', '.gitignore - Git ignore rules'),
        ('backend/app.py', 'backend/app.py - Flask application'),
        ('backend/__init__.py', 'backend/__init__.py - Package init'),
    ]
    
    for filename, description in required_files:
        filepath = os.path.join(base_path, filename)
        if not check_file(filepath, description):
            all_good = False
    
    # Check Procfile content
    print(f"\n{YELLOW}[2/4] Checking Procfile configuration...{RESET}")
    procfile_path = os.path.join(base_path, 'Procfile')
    if check_content(procfile_path, 'gunicorn', 'Procfile contains gunicorn'):
        if check_content(procfile_path, 'backend', 'Procfile references backend directory'):
            pass
        else:
            all_good = False
    else:
        all_good = False
    
    # Check requirements.txt
    print(f"\n{YELLOW}[3/4] Checking dependencies in requirements.txt...{RESET}")
    req_file = os.path.join(base_path, 'requirements.txt')
    dependencies = [
        ('Flask', 'Flask'),
        ('gunicorn', 'gunicorn'),
        ('supabase', 'supabase'),
        ('PyPDF2', 'PyPDF2'),
        ('python-dotenv', 'python-dotenv'),
    ]
    
    for dep_name, dep_display in dependencies:
        if not check_content(req_file, dep_name, f'{dep_display} in requirements.txt'):
            all_good = False
    
    # Check git configuration
    print(f"\n{YELLOW}[4/4] Checking Git configuration...{RESET}")
    git_dir = os.path.join(base_path, '.git')
    if os.path.isdir(git_dir):
        print(f"{GREEN}✓{RESET} Git repository initialized")
    else:
        print(f"{RED}✗{RESET} Git repository NOT initialized")
        print(f"   Run: {BLUE}git init{RESET}")
        all_good = False
    
    gitignore_path = os.path.join(base_path, '.gitignore')
    if check_content(gitignore_path, '.env', '.gitignore excludes .env files'):
        if check_content(gitignore_path, '*.pdf', '.gitignore excludes PDF files'):
            pass
        else:
            all_good = False
    else:
        all_good = False
    
    # Final summary
    print(f"\n{BLUE}{'='*60}")
    if all_good:
        print(f"{GREEN}✓ ALL CHECKS PASSED - READY FOR DEPLOYMENT!{RESET}")
        print(f"{'='*60}{RESET}\n")
        print(f"{BLUE}Next steps:{RESET}")
        print(f"1. Run: {BLUE}git add .{RESET}")
        print(f"2. Run: {BLUE}git commit -m 'Deploy to Render'{RESET}")
        print(f"3. Run: {BLUE}git push origin main{RESET}")
        print(f"4. Go to render.com and create new Web Service")
        print(f"5. Connect your GitHub repository")
        print(f"6. Add environment variables in Render Dashboard")
        print(f"7. Click 'Create Web Service' to deploy\n")
        return 0
    else:
        print(f"{RED}✗ SOME CHECKS FAILED - FIX ISSUES BEFORE DEPLOYING!{RESET}")
        print(f"{'='*60}{RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
