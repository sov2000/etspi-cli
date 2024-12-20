import json
import click

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes
from etspi.etsyv3.models import UpdateListingInventoryRequest

def update_listing_iv(ctx: Any, id: str, src_file: Any, silent: bool) -> None:
    ctx.vlog(f"Update IV Action for Listing ID: {id}")
    pld = json.load(src_file)
    etsy = ctx.get_etsy("LISTING-UPDATE-IV")
    if "type" in pld:
         pld["listing_type"] = pld["type"]
         del(pld["type"])
    listing_iv = UpdateListingInventoryRequest(**pld)
    res = etsy.update_listing_inventory(id, listing_iv)
    if not silent:
        print(res)
    return

@click.command("listing-update-iv", short_help="Update a listing by ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("-f", "--src-file", required=True, help="Source file from which to read JSON to update listing inventory.",
              type=click.File(mode="r", encoding="utf-8", errors="strict", lazy=None, atomic=False))
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, id, src_file, silent):
    """Perform an Update action on a listing by its ID."""
    ctx.check_auth("LISTING-UPDATE-IV")
    if not id is None:
        ctx.vlog(f"Process listing: {id}")
    try:
        update_listing_iv(ctx, id, src_file, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
