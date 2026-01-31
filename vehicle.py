#!/usr/bin/env python3
# Ishan Gugale - Vehicle Info Tool
# Created by: ishan58775
# Instagram: ishan58775

"""
DISCLAIMER:
This tool is for EDUCATIONAL and ETHICAL USE ONLY.
Unauthorized tracking, surveillance or background searches
without permission may be ILLEGAL. Use responsibly.
"""

import sys
import os
import json
import time
import hashlib
import requests
import argparse
import re
from urllib.parse import urlencode
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from datetime import datetime

# ==================== CONFIGURATION ====================
# [API SETUP] - Reverted to your original Vercel API
# This API is free and does not require a specific key.
API_BASE = "https://vehicleinfobyterabaap.vercel.app/lookup"

# Branding & Version
VERSION = "3.0 PRO (Ishan Edition)"
INSTAGRAM = "ishan58775"

# Stealth User Agent (iPhone 15 Pro)
# We keep this to make the request look like a real mobile phone
USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"

console = Console()

# ==================== UTILITIES ====================
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def ensure_dirs():
    os.makedirs("results", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("cache", exist_ok=True)

def log(msg):
    with open("logs/ishan_tool.log", "a") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

def clean_rc(rc_input):
    """Removes special characters and spaces from RC number."""
    if not rc_input:
        return ""
    # Keep alphanumeric only
    return re.sub(r'[^A-Za-z0-9]', '', rc_input).upper()

# ==================== CACHING SYSTEM ====================
def cache_path(rc):
    return f"cache/{hashlib.md5(rc.encode()).hexdigest()}.json"

def save_cache(rc, data):
    try:
        with open(cache_path(rc), "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass

def load_cache(rc):
    path = cache_path(rc)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return None
    return None

# ==================== API HANDLER ====================
def fetch_vehicle_data(rc):
    # 1. Check Cache
    cached = load_cache(rc)
    if cached:
        return cached, True

    # 2. Setup Request
    # The Vercel API uses GET method with 'rc' parameter
    params = {"rc": rc}
    url = f"{API_BASE}?{urlencode(params)}"
    
    headers = {
        "User-Agent": USER_AGENT
    }

    start = time.time()
    
    # 3. Execute Request
    try:
        with Progress(
            SpinnerColumn(style="bold cyan"), 
            TextColumn("[bold cyan]{task.description}"),
            transient=True
        ) as progress:
            progress.add_task(description=f"Fetching details for {rc}...", total=None)
            
            # Using standard GET request for this API
            resp = requests.get(
                url,
                headers=headers,
                timeout=25
            )
            
    except Exception as e:
        return {"error": str(e)}, False

    duration = round((time.time() - start) * 1000, 2)

    # 4. Validate Response
    if resp.status_code != 200:
        return {"error": f"HTTP {resp.status_code} – Server Error (Try again later)"}, False

    try:
        data = resp.json()
    except:
        return {"error": "Invalid JSON returned. API might be down."}, False

    data["_api_time"] = duration
    save_cache(rc, data)
    return data, False

# ==================== OUTPUT HANDLERS ====================
def export_json(rc, data):
    path = f"results/{rc}.json"
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def display_results(rc, data, from_cache):
    # BRANDING HEADER
    tool_info = f"[bold magenta]ISHAN GUGALE TOOL[/bold magenta] • [bold magenta]Instagram: {INSTAGRAM}[/bold magenta]"
    console.print(Panel(tool_info, style="magenta", expand=False))

    if "error" in data:
        console.print(Panel(f"[bold red]Error:[/bold red] {data['error']}", style="red"))
        return

    # Clean internal keys
    display_data = {k: v for k, v in data.items() if not k.startswith("_")}
    api_time = data.get("_api_time", "N/A")

    # Status Panel
    status = Panel(
        f"[bold green]STATUS: SUCCESS[/bold green]\nCached: {'YES' if from_cache else 'NO'}\nTime: {api_time} ms",
        style="green",
        expand=False,
    )
    console.print(status)

    # Main Data Table
    table = Table(
        title=f"Vehicle RC Info — {rc}",
        box=box.ROUNDED,
        show_lines=True,
    )
    table.add_column("Field", style="bold cyan", no_wrap=True)
    table.add_column("Value", style="white")

    for k, v in display_data.items():
        # Handle potential nested lists or dicts
        if isinstance(v, (dict, list)):
            v = str(v)
        table.add_row(k.replace("_", " ").title(), str(v))

    console.print(table)
    console.print("\n[dim]Result saved to 'results/' folder.[/dim]")

    # BRANDING FOOTER
    console.print(
        Panel(
            Align.center(f"Created by: {INSTAGRAM}\nInstagram: {INSTAGRAM}", vertical="middle"),
            style="blue",
        )
    )

# ==================== UI / BANNER ====================
def loading_animation():
    console.print(f"\n[bold green]Initializing {INSTAGRAM} Tool...[/bold green]\n")
    steps = ["Loading modules", f"Verifying {INSTAGRAM} connection", "Starting system"]
    for step in steps:
        console.print(f"[bold cyan]>> {step}...[/bold cyan]")
        time.sleep(0.3)
    time.sleep(0.4)

def banner():
    console.rule()
    console.print(Align.center(f"[bold red]ISHAN GUGALE[/bold red] • [yellow]{VERSION}[/yellow]"))
    console.print(Align.center(f"[green]Created by: {INSTAGRAM} • Instagram: {INSTAGRAM}[/green]"))
    console.rule()
    console.print(
        Panel(
            "[bold white on red] DISCLAIMER [/bold white on red]\nThis tool is for lawful, educational use only.",
            style="red",
            expand=False,
        )
    )
    console.rule()

# ==================== MAIN ====================
def process_rc(rc):
    rc = clean_rc(rc)
    if len(rc) < 4:
        console.print("[red]Invalid RC format.[/red]")
        return

    log(f"Processing: {rc}")
    data, cached = fetch_vehicle_data(rc)
    display_results(rc, data, cached)
    
    if "error" not in data:
        export_json(rc, data)

def main():
    ensure_dirs()
    clear_screen()
    loading_animation()
    banner()

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rc", help="RC Number")
    parser.add_argument("-f", "--file", help="Bulk File")
    args = parser.parse_args()

    if args.file:
        if os.path.exists(args.file):
            with open(args.file, "r") as f:
                rc_list = [line.strip() for line in f if line.strip()]
            console.print(f"[cyan]Loaded {len(rc_list)} numbers for bulk check...[/cyan]\n")
            for rc in rc_list:
                process_rc(rc)
                time.sleep(1) # Safety delay
    elif args.rc:
        process_rc(args.rc)
    else:
        console.print("[bold cyan]Enter Vehicle No (RC):[/bold cyan] ", end="")
        rc = input().strip()
        if rc:
            process_rc(rc)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Exiting...[/red]")
        sys.exit(0)
