#!/usr/bin/env python3
"""
Allure History Updater - PowerShell compatible with verbose output
Handles history-trend.json buildOrder incrementation and history management
"""

import json
import os
import sys
import argparse
from pathlib import Path

def log_message(message, verbose=True):
    """Print message with timestamp for GitHub Actions UI"""
    if verbose:
        print(f"[{os.times().user:.3f}s] {message}")

def update_allure_history(verbose=True):
    log_message("Starting Allure history update...", verbose)
    
    # Path to history files
    history_dir = Path('./allure-results/history')
    trend_file = history_dir / 'history-trend.json'
    history_file = history_dir / 'history.json'
    
    # Ensure directory exists
    history_dir.mkdir(exist_ok=True)
    log_message(f"Ensured directory exists: {history_dir}", verbose)
    
    # Initialize or load history-trend.json
    if trend_file.exists():
        try:
            with open(trend_file, 'r', encoding='utf-8') as f:
                history_trend = json.load(f)
            # Find max buildOrder
            if history_trend and isinstance(history_trend, list):
                max_order = max(item.get('buildOrder', 0) for item in history_trend)
                log_message(f"Found {len(history_trend)} existing history entries", verbose)
            else:
                history_trend = []
                max_order = 0
                log_message("History file exists but is empty or invalid", verbose)
            log_message(f"Max buildOrder found: {max_order}", verbose)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            log_message(f"Error loading history: {e}, creating new history", verbose)
            history_trend = []
            max_order = 0
    else:
        log_message("No existing history file found, creating new history", verbose)
        history_trend = []
        max_order = 0
    
    # Create new entry
    new_order = max_order + 1
    new_entry = {
        'buildOrder': new_order,
        'reportName': f'Run #{new_order}',
        'reportUrl': f'https://github.com/{os.environ.get("GITHUB_REPOSITORY", "")}/actions/runs/{os.environ.get("GITHUB_RUN_ID", "")}',
        'data': {
            'failed': 0, 'broken': 0, 'skipped': 0, 
            'passed': 0, 'unknown': 0, 'total': 0
        }
    }
    
    log_message(f"Creating new entry with buildOrder: {new_order}", verbose)
    
    # Add new entry and keep only last 10 runs
    history_trend.append(new_entry)
    history_trend = history_trend[-10:]  # Keep only recent history
    log_message(f"History now contains {len(history_trend)} entries", verbose)
    
    # Save updated history
    with open(trend_file, 'w', encoding='utf-8') as f:
        json.dump(history_trend, f, indent=2, ensure_ascii=False)
    log_message(f"Saved updated history to: {trend_file}", verbose)
    
    # Ensure history.json exists
    if not history_file.exists():
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2, ensure_ascii=False)
        log_message(f"Created empty history.json: {history_file}", verbose)
    else:
        log_message(f"history.json already exists: {history_file}", verbose)
    
    # Print final summary for GitHub UI
    print("=" * 60)
    print("O ALLURE HISTORY UPDATE SUMMARY")
    print("=" * 60)
    print(f"OK. New buildOrder: {new_order}")
    print(f"OK Total history entries: {len(history_trend)}")
    print(f"OK. History files updated:")
    print(f"   - {trend_file}")
    print(f"   - {history_file}")
    
    if verbose and len(history_trend) > 0:
        print(f"OK. Latest entries:")
        for entry in history_trend[-3:]:  # Show last 3 entries
            print(f"   - Build {entry['buildOrder']}: {entry['reportName']}")
    
    print("=" * 60)
    
    return new_order

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update Allure history files')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-s', '--silent', action='store_true', help='Enable silent mode')
    
    args = parser.parse_args()
    verbose = args.verbose and not args.silent
    
    try:
        update_allure_history(verbose=verbose)
        sys.exit(0)
    except Exception as e:
        print(f"FAIL: CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)