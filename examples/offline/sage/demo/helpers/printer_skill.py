from examples.offline.sage.demo.helpers.printer_banner import _banner


def _print_skill(label: str, text: str, max_lines: int = 35, console=None) -> None:
    _banner(label, console=console)
    lines = text.strip().splitlines()
    for line in lines[:max_lines]:
        console.print(line)
    if len(lines) > max_lines:
        console.print(f"  … ({len(lines) - max_lines} more lines not shown)")
