import jwt
import base64
import json
import datetime
from rich import print
from rich.table import Table
from rich.panel import Panel
from rich.console import Console

console = Console()

def decode_jwt(token):
    try:
        # Split JWT token
        parts = token.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid JWT format!")

        header_b64, payload_b64, _ = parts  # Ignore signature

        # Decode JWT header & payload
        header = json.loads(base64.urlsafe_b64decode(header_b64 + "==").decode('utf-8'))
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "==").decode('utf-8'))

        # Extract timestamps
        timestamps = {
            "auth_time": payload.get("auth_time"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat"),
        }

        # Convert timestamps
        formatted_times = {
            key: datetime.datetime.utcfromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S UTC') if value else "N/A"
            for key, value in timestamps.items()
        }

        # Expiry check
        current_time = datetime.datetime.utcnow().timestamp()
        is_expired = current_time > timestamps["exp"] if timestamps["exp"] else False
        token_validity = (timestamps["exp"] - timestamps["iat"]) / 3600 if timestamps["exp"] and timestamps["iat"] else "N/A"

        # Security Checks
        security_checks = []
        if is_expired:
            security_checks.append("[red]❌ Token has expired![/red]")
        else:
            security_checks.append("[green]✅ Token is valid[/green]")

        if not timestamps["exp"]:
            security_checks.append("[red]❌ Missing exp (Expiration) claim![/red]")
        else:
            security_checks.append("[green]✅ exp Claim Exists[/green]")

        if token_validity != "N/A" and token_validity < 1:
            security_checks.append("[yellow]⚠️ Token is valid for less than 1 hour.[/yellow]")

        # Print results
        console.print(Panel("[bold magenta]🔍 JWT Security Analyzer[/bold magenta]"))

        # Print Header & Payload
        console.print("\n[bold cyan]Header:[/bold cyan]", json.dumps(header, indent=2))
        console.print("\n[bold cyan]Payload:[/bold cyan]", json.dumps(payload, indent=2))

        # Display Table
        table = Table(title="[bold cyan]JWT Information[/bold cyan]", expand=True)
        table.add_column("Field", style="bold cyan")
        table.add_column("Value", style="bold yellow")

        for key, value in formatted_times.items():
            table.add_row(f"🔹 {key.replace('_', ' ').title()}", value)
        table.add_row("🔹 Token Validity", f"{token_validity:.2f} hours" if isinstance(token_validity, float) else "N/A")

        console.print("\n", table)

        # Print Security Checks
        console.print("\n[bold cyan]🔎 Security Checks Performed:[/bold cyan]")
        for check in security_checks:
            console.print(check)

    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")

# Example: Paste your JWT token here
jwt_token = input("Enter JWT Token: ")
decode_jwt(jwt_token)
