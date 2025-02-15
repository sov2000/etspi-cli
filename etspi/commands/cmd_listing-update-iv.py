import json
import click

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.util import listfileio
from etspi.etsyv3 import EtsyAPI, Includes
from etspi.etsyv3.models import UpdateListingInventoryRequest

def update_listing_iv(ctx: Any, id: int, src_file: Any, format: str, silent: bool) -> None:
    ctx.vlog(f"Update IV Action for Listing ID: {id}")
    #pld = json.load(src_file)
    pld = listfileio.load_listing_file(ctx, None, format, src_file)
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
@click.option("-F", "--format", required=False, default="JSON", 
              type=click.Choice(["JSON", "YAML"], case_sensitive=False), multiple=False, help="Set format to JSON or YAML for input file.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, id, src_file, format, silent):
    """Perform an Update action on a listing by its ID."""
    result = 0
    ctx.check_auth("LISTING-UPDATE-IV")
    if not id is None:
        ctx.vlog(f"Process listing: {id}")
    try:
        update_listing_iv(ctx, id, src_file, format, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
        result = 1
    return result
