import json
import click
import jmespath

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes
from etspi.etsyv3.models import UpdateListingInventoryRequest

def get_listing_inventory(ctx: Any, id: int, transform: str, query: str, out: Any, silent: bool) -> None:
    ctx.vlog(f"Get Inventroy Action for Listing ID: {id}")
    etsy = ctx.get_etsy("LISTING-GET-IV")
    res = etsy.get_listing_inventory(id)
    if transform == "update":
        res = UpdateListingInventoryRequest.generate_request_from_inventory_response(res).get_dict()
    if res:
        if query:
            res = jmespath.search(query, res)        
        if out:
            out.write(json.dumps(res, indent=4))
        if not silent:
            print(res)
    return

@click.command("listing-get-iv", short_help="Retrieve or Get a listing inventory by ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("--format-update", "transform", flag_value="update", default=False, help="Transform listing response into format suitable for listing update request.")
@click.option("-q", "--query", type=click.STRING, help="JMESPath query to filter the output of the command.")
@click.option("-o", "--out", required=False, type=click.File(mode="w", encoding="utf-8", errors="strict", lazy=None, atomic=False), help="Also output result into a file")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, id, transform, query, out, silent):
    """Perform a Get inventory action on a listing by its ID."""
    ctx.check_auth("LISTING-GET-IV")
    if not id is None:
        ctx.vlog(f"Process GET IV listing: {id}")
    try:
        get_listing_inventory(ctx, id, transform, query, out, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
