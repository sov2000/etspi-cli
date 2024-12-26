import json
import click

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes
from etspi.etsyv3.models import UpdateListingPropertyRequest

def update_listing_props(ctx: Any, id: int, shop_id: int, prop_id: int, src_file: Any, silent: bool) -> None:
    ctx.vlog(f"Update Properties Action for Listing ID: {id} Property ID: {prop_id}")
    pld = json.load(src_file)
    etsy = ctx.get_etsy("PROP-UPDATE")
    prop = UpdateListingPropertyRequest(**pld)
    res = etsy.update_listing_property(shop_id, id, prop_id, prop)
    if not silent:
        print(res)
    return

@click.command("prop-update", short_help="Update listing Property by Listing ID and Property ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("-s", "--shop-id", required=True, default=0, type=click.INT, help="Shop ID to use to update Property ID specified.")
@click.option("-pi", "--prop-id", required=True, default=0, type=click.INT, help="Listing Property ID to update.")
@click.option("-f", "--src-file", required=True, help="Source file from which to read JSON to update property.",
              type=click.File(mode="r", encoding="utf-8", errors="strict", lazy=None, atomic=False))
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, id, shop_id, prop_id, src_file, silent):
    """Perform a Update Property action on a listing by its ID."""
    ctx.check_auth("PROP-UPDATE")
    if not id is None:
        ctx.vlog(f"Process Update listing properties: {id}")
    try:
        update_listing_props(ctx, id, shop_id, prop_id, src_file, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
