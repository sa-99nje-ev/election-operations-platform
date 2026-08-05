"""
Election Operations Platform - End-to-End Verification Walkthrough
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

# Load local environment configuration
load_dotenv()

console = Console()

# Configuration Parameters from .env
BASE_URL = f"http://127.0.0.1:{os.getenv('API_PORT', '8000')}"
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin_user")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "AdminPassword123")


def log_step(title: str):
    console.print(f"\n[bold cyan]► {title}[/bold cyan]")


def run_demo():
    console.print(
        Panel.fit(
            "[bold white]ELECTION OPERATIONS PLATFORM[/bold white]\n"
            "[dim]Automated System Verification & Integrity Walkthrough[/dim]",
            border_style="magenta",
        )
    )

    # 1. Healthcheck Verification
    log_step("Checking System Gateway & Infrastructure Health")
    try:
        health_res = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_res.status_code == 200:
            console.print("[bold green]✔[/bold green] System Gateway & Infrastructure online.")
        else:
            console.print(f"[bold red]✘ Healthcheck failed:[/bold red] HTTP {health_res.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        console.print("[bold red]✘ Connection error:[/bold red] Ensure FastAPI is running on port 8000.")
        sys.exit(1)

    # 2. Authentication Protocol
    log_step(f"Authenticating as Administrator ({ADMIN_USERNAME})")
    
    # Try Form Data (OAuth2 standard) first
    auth_response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        timeout=5,
    )

    # Fallback to JSON payload if OAuth2 form fails
    if auth_response.status_code == 422:
        auth_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            timeout=5,
        )

    if auth_response.status_code != 200:
        console.print(f"[bold red]❌ Authentication failed:[/bold red] {auth_response.text}")
        sys.exit(1)

    token_data = auth_response.json()
    access_token = token_data.get("access_token")
    console.print(f"[bold green]✔[/bold green] Authenticated successfully as '{ADMIN_USERNAME}'.")

    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. System Entities Verification
    log_step("Fetching System Dashboard / Status")
    try:
        status_res = requests.get(f"{BASE_URL}/admin/status", headers=headers, timeout=5)
        if status_res.status_code == 200:
            console.print("[bold green]✔[/bold green] Retrieved admin operations dashboard state.")
        else:
            console.print(f"[yellow]i Dashboard endpoint returned HTTP {status_res.status_code}[/yellow]")
    except Exception as err:
        console.print(f"[yellow]i Skipped optional status endpoint check: {err}[/yellow]")

    console.print("\n[bold green]====================================================[/bold green]")
    console.print("[bold green]✔ Platform verification walkthrough completed![/bold green]")
    console.print("[bold green]====================================================[/bold green]\n")


if __name__ == "__main__":
    run_demo()