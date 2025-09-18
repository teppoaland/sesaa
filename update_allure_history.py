#!/usr/bin/env python3
"""
Allure History Manager - PowerShell compatible with verbose output
1. Verifies the history directory structure.
2. Checks if previous history was downloaded successfully from the artifact.
3. Manages history-trend.json buildOrder incrementation.
"""

import json
import os
import sys
import argparse
from pathlib import Path

def log_message(message, verbose=True):
    """Print message for GitHub Actions UI"""
    if verbose:
        print(f"[ALLURE-HISTORY] {message}")
        sys.stdout.flush()

def clean_history_trend(history_trend):
    """Clean and validate history trend entries"""
    cleaned = []
    for entry in history_trend:
        # Only keep entries with proper buildOrder structure
        if isinstance(entry, dict) and 'buildOrder' in entry and 'data' in entry:
            # Ensure all required fields exist
            if all(key in entry for key in ['buildOrder', 'reportName', 'reportUrl', 'data']):
                cleaned.append(entry)
    return cleaned

def manage_allure_history(verbose=True):
    log_message("Starting complete Allure history management...", verbose)
    
    # Path to history files
    history_dir = Path('./allure-results/history')
    trend_file = history_dir / 'history-trend.json'
    history_file = history_dir / 'history.json'
    
    # 1. Ensure the directory exists
    history_dir.mkdir(parents=True, exist_ok=True)
    log_message(f"Ensured directory exists: {history_dir}", verbose)
    
    # 2. CHECK if history was downloaded from git storage
    downloaded_files = list(history_dir.glob('*.json'))
    history_downloaded = len(downloaded_files) > 0
    
    if history_downloaded:
        log_message("SUCCESS: History files found from git storage download.", verbose)
        for file in downloaded_files:
            log_message(f"   - Found: {file.name}", verbose)
    else:
        log_message("INFO: No history files found. This is expected on the first run.", verbose)
    
    # 3. Initialize or load history-trend.json
    if trend_file.exists():
        try:
            with open(trend_file, 'r', encoding='utf-8') as f:
                raw_history = json.load(f)
            
            # Clean the history data
            history_trend = clean_history_trend(raw_history)
            
            if history_trend:
                # Find max buildOrder from valid entries
                max_order = max(item.get('buildOrder', 0) for item in history_trend)
                log_message(f"Loaded and cleaned history trend with {len(history_trend)} valid entries. Max buildOrder: {max_order}", verbose)
                log_message(f"Removed {len(raw_history) - len(history_trend)} invalid entries.", verbose)
            else:
                # No valid entries found
                history_trend = []
                max_order = 0
                log_message("No valid entries found in existing history. Starting fresh.", verbose)
                
        except (json.JSONDecodeError, Exception) as e:
            log_message(f"Error loading {trend_file}: {e}. Creating new history.", verbose)
            history_trend = []
            max_order = 0
    else:
        # No trend file exists (first run or download failed)
        log_message("No history-trend.json file found. Creating new history.", verbose)
        history_trend = []
        max_order = 0
    
    # 4. Create new entry for THIS run
    new_order = max_order + 1
    new_entry = {
        'buildOrder': new_order,
        'reportName': f'Run #{new_order}',
        'reportUrl': f'https://github.com/{os.environ.get("GITHUB_REPOSITORY", "user/repo")}/actions/runs/{os.environ.get("GITHUB_RUN_ID", "1")}',
        'data': { 
            # Placeholder data - Allure will fill this after report generation
            'failed': 0, 'broken': 0, 'skipped': 0, 
            'passed': 0, 'unknown': 0, 'total': 0
        }
    }
    
    log_message(f"Creating new trend entry with buildOrder: {new_order}", verbose)
    
    # Add new entry and keep only recent history (last 10 runs)
    history_trend.append(new_entry)
    history_trend = history_trend[-10:]  # Keep only last 10 runs
    log_message(f"History trend now contains {len(history_trend)} entries.", verbose)
    
    # 5. Save the updated and cleaned trend file
    with open(trend_file, 'w', encoding='utf-8') as f:
        json.dump(history_trend, f, indent=2, ensure_ascii=False)
    log_message(f"Saved cleaned and updated history trend to: {trend_file}", verbose)
    
    # 6. Create other required Allure history files
    duration_trend_file = history_dir / 'duration-trend.json'
    categories_trend_file = history_dir / 'categories-trend.json'
    
    # Create duration trend if it doesn't exist
    if not duration_trend_file.exists():
        with open(duration_trend_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        log_message(f"Created duration trend file: {duration_trend_file}", verbose)
    
    # Create categories trend if it doesn't exist
    if not categories_trend_file.exists():
        with open(categories_trend_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        log_message(f"Created categories trend file: {categories_trend_file}", verbose)
    
    # 7. Ensure history.json exists (required by Allure)
    if not history_file.exists():
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2, ensure_ascii=False)
        log_message(f"Created required history file: {history_file}", verbose)
    else:
        log_message(f"Verified required file exists: {history_file}", verbose)
    
    # 8. Final summary for clear logging in GitHub UI
    print("\n" + "="*70)
    print("ALLURE HISTORY MANAGEMENT SUMMARY")
    print("="*70)
    print(f"Status: {'HISTORY DOWNLOADED & CLEANED' if history_downloaded else 'FRESH START (No previous history)'}")
    print(f"New Build Order: {new_order}")
    print(f"Total Valid History Entries: {len(history_trend)}")
    print(f"Files in ./allure-results/history/:")
    for file in history_dir.iterdir():
        if file.is_file():
            print(f"   - {file.name} ({file.stat().st_size} bytes)")
    print("="*70)
    
    return new_order

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Manage and update Allure history files')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-s', '--silent', action='store_true', help='Enable silent mode (overrides verbose)')
    parser.add_argument('--clean', action='store_true', help='Clean invalid entries from existing history')
    
    args = parser.parse_args()
    verbose = args.verbose and not args.silent
    
    try:
        manage_allure_history(verbose=verbose)
        log_message("Allure history management completed successfully.", verbose)
        sys.exit(0)
    except Exception as e:
        log_message(f"CRITICAL ERROR: {e}", True)
        import traceback
        traceback.print_exc()
        sys.exit(1)