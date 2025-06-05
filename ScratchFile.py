from rich.console import Console
from rich.table import Table

console = Console()

table = Table(show_header=True, header_style="bold magenta")
table.add_column("S/N", style="dim", width=3)
table.add_column("DNV Tables", width=12)
table.add_column("Description", width=20, justify="full")
table.add_column("Use Case", justify="left")

table.add_row("1", "EV_xxxxxx", "Environmental Values", "For Pipe Quality")
table.add_row(
    "2",
    "GEN_xxxxxx",
    "General Values from Haul off",
    "Pipe Directional Process",)

table.add_row(
    "3",
    "RC_xxxxx",
    "Ram Counter",
    "Critical Quality Indicator",)

console.print(table)