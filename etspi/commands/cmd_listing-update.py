import json
import click

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.util import listfileio
from etspi.etsyv3 import EtsyAPI, Includes
from etspi.etsyv3.models import UpdateListingRequest

def update_listing(ctx: Any, id: int, shop_id: int, src_file: Any, format: str, silent: bool) -> None:
    ctx.vlog(f"Update Action for Listing ID: {id}")
    #pld = json.load(src_file)
    pld = listfileio.load_listing_file(ctx, None, format, src_file)
    etsy = ctx.get_etsy("LISTING-UPDATE")
    if "type" in pld:
         pld["listing_type"] = pld["type"]
         del(pld["type"])
    listing = UpdateListingRequest(**pld)
    res = etsy.update_listing(shop_id, id, listing)
    if not silent:
        print(res)
    return

@click.command("listing-update", short_help="Update a listing by ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("-s", "--shop-id", required=False, type=click.INT, help="Shop ID to use for update and other actions.")
@click.option("-f", "--src-file", required=True, help="Source file from which to read JSON to update a listing.",
              type=click.File(mode="r", encoding="utf-8", errors="strict", lazy=None, atomic=False))
@click.option("-F", "--format", required=False, default="JSON", 
              type=click.Choice(["JSON", "YAML"], case_sensitive=False), multiple=False, help="Set format to JSON or YAML for input file.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, id, shop_id, src_file, format, silent) -> int:
    """Perform an Update action on a listing by its ID."""
    result = 0
    ctx.check_auth("LISTING-UPDATE")
    if not id is None:
        ctx.vlog(f"Process listing: {id}")
    try:
        update_listing(ctx, id, shop_id, src_file, format, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
        result = 1
    return result