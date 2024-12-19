import json
import click
import jmespath

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etsyv3 import EtsyAPI, Includes
from etsyv3.models import CreateDraftListingRequest, UpdateListingRequest

def get_listing(ctx: Any, id: str, includes: List, transform: str, query: str, out: Any, silent: bool) -> None:
    ctx.vlog(f"Get Action for Listing ID: {id}")
    etsy = ctx.get_etsy("LISTING-GET")
    res = etsy.get_listing(id, includes)
    if transform == "draft":
        res = CreateDraftListingRequest.generate_request_from_listing_response(res).get_dict()
    elif transform == "update":
        res = UpdateListingRequest.generate_request_from_listing_response(res).get_dict()
    if res:
        if query:
            res = jmespath.search(query, res)
        if out:
            out.write(json.dumps(res, indent=4))
        if not silent:
            print(res)
    return

@click.command("listing-get", short_help="Retrieve or Get a listing by ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("-in", "--include", type=click.Choice([Includes.SHIPPING.value, Includes.IMAGES.value, Includes.SHOP.value, Includes.USER.value, Includes.TRANSLATIONS.value, Includes.INVENTORY.value, Includes.VIDEOS.value], case_sensitive=False), multiple=True)
#@click.option("-t", "--transform", is_flag=True, default=False, help="Transform listing response into format suitable for create or update request.")
@click.option("--format-draft", "transform", flag_value="draft", default=False, help="Transform listing response into format suitable for listing draft request.")
@click.option("--format-update", "transform", flag_value="update", default=False, help="Transform listing response into format suitable for listing update request.")
@click.option("-q", "--query", type=click.STRING, help="JMESPath query to filter the output of the command.")
@click.option("-o", "--out", required=False, type=click.File(mode="w", encoding="utf-8", errors="strict", lazy=None, atomic=False), help="Also output result into a file")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, id, include, transform, query, out, silent):
    """Perform a GET action on a listing by its ID."""
    ctx.check_auth("LISTING-GET")
    if not id is None:
        ctx.vlog(f"Process GET listing: {id}")
    try:
        incs = None
        if include:
            incs = [Includes(i) for i in include]
        get_listing(ctx, id, incs, transform, query, out, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
