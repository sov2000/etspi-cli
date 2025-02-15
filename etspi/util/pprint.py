import os
import sys

from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.padding import Padding

def context_pprint(content: Any) -> str:
    console = Console()
    out = ""
    with console.capture() as capture:
        console.print(content)
    out = capture.get()
    return out