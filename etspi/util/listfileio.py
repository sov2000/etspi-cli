import json
import yaml
import os
import glob

from typing import Any, Dict, List, Optional

# load the listing file from either json or yaml format by path and return the listing object
def load_listing_file(ctx: Any, file: str) -> Dict:
    listing = {}
    with open(file, 'r', encoding="utf-8") as f:
        if file.endswith(".ejs"):
            listing = json.load(f)
        else:
            listing = yaml.safe_load(f)
    return listing

def save_listing_file(ctx: Any, listing: Dict, file: str = None, format: str = "JSON", stream: Any = None) -> None:
    if listing:
        f = stream
        if stream is None:
            f = open(file, 'w', encoding="utf-8")
        if format == "YAML":
            yaml.dump(listing, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        else:
            f.write(json.dumps(listing, indent=4))
        if stream is None:
            f.close()
    else:
        raise Exception("Failed to save listing - object is empty.")

def scan_local_root(ctx: Any, root: str, fmt_list: List) -> List:
    ctx.vlog(f"Scan Local Root: {root}")
    listing_files = []
    for ext in fmt_list: # loop over the extensions
        scan_files = glob.glob(os.path.join(root, "**", ext), recursive=True) # find files recursively
        if scan_files:
            listing_files.extend(scan_files)
    return listing_files