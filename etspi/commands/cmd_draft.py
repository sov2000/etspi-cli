import json
import click

from typing import Any, Dict, List, Optional
from rich import print
from rich.console import Console
from rich.panel import Panel
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes
from etspi.etsyv3.models import CreateDraftListingRequest

def draft_listing(ctx: Any, shop_id: int, src_file: Any, silent: bool) -> None:
    pld = json.load(src_file)
    etsy = ctx.get_etsy("DRAFT")
    if "type" in pld:
        pld["listing_type"] = pld["type"]
        del(pld["type"])
    listing = CreateDraftListingRequest(**pld)
    res = etsy.create_draft_listing(shop_id, listing)
    if not silent:
        print(res)
    return

@click.command("draft", short_help="Retrieve listing by ID")
@click.option("-s", "--shop-id", required=True, type=click.INT, help="Shop ID to use where to create a new draft.")
@click.option("-f", "--src-file", required=True, help="Source file from which to read JSON to create a new draft",
              type=click.File(mode="r", encoding="utf-8", errors="strict", lazy=None, atomic=False))
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output")
@pass_environment
def cli(ctx, shop_id, src_file, silent):
    """Create a new listing draft."""
    ctx.check_auth("DRAFT")
    if not shop_id is None and not src_file is None:
        ctx.vlog(f"Create draft listing: {shop_id} from {src_file}")
    try:
        draft_listing(ctx, shop_id, src_file, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
