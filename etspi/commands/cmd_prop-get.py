import json
import click
import jmespath

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.util import listfileio, pprint
from etspi.etsyv3 import EtsyAPI, Includes
from etspi.etsyv3.models import UpdateListingPropertyRequest

def get_listing_props(ctx: Any, id: int, shop_id: int, prop_id: int, query: str, out: Any, format: str, transform: bool, silent: bool) -> None:
    ctx.vlog(f"Get Properties Action for Listing ID: {id}")
    etsy = ctx.get_etsy("PROP-GET")
    if prop_id > 0:
        # res = etsy.get_listing_property(id, prop_id) - not implemented by Etsy API at the moment
        res_full = etsy.get_listing_properties(shop_id, id)
        for result in res_full['results']:
            if result['property_id'] == prop_id:
                res = result
        if res and transform == "update":
            res = UpdateListingPropertyRequest.generate_request_from_listing_property_response(res).get_dict()
    elif shop_id > 0:
        res = etsy.get_listing_properties(shop_id, id)
        if res and transform == "update":
            prop_list = [UpdateListingPropertyRequest.generate_request_from_listing_property_response(r, r["property_id"]).get_dict() for r in res['results']]
            res = { "properties": prop_list }
    else:
        raise click.BadArgumentUsage("No Shop ID or Property Id provided to retrieve listing property(ies).") 
    if res:
        if query:
            res = jmespath.search(query, res)
        if out:
            listfileio.save_listing_file(ctx, res, None, format, out)
        if not silent:
            print(res)
    return

@click.command("prop-get", short_help="Retrieve or Get all listing Properties by Listing ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("-s", "--shop-id", required=True, default=0, type=click.INT, help="Shop ID to use to retrieve listing properties, required if no Property ID specified.")
@click.option("-pi", "--prop-id", required=False, default=0, type=click.INT, help="Listing Property ID to retrieve or, if omitted or 0, get all properties.")
@click.option("-q", "--query", type=click.STRING, help="JMESPath query to filter the output of the command.")
@click.option("-o", "--out", required=False,
              type=click.File(mode="w", encoding="utf-8", errors="strict", lazy=None, atomic=False), help="Also output result into a file")
@click.option("-F", "--format", required=False, default="JSON", 
              type=click.Choice(["JSON", "YAML"], case_sensitive=False), multiple=False, help="Set format to JSON or YAML for output file.")
@click.option("--format-update", "transform", flag_value="update", default=False, help="Transform property response into format suitable for listing property update request.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, id, shop_id, prop_id, query, out, format, transform, silent):
    """Perform a GET Properties action on a listing by its ID."""
    result = 0
    ctx.check_auth("PROP-GET")
    if not id is None:
        ctx.vlog(f"Process GET listing properties: {id}")
    try:
        get_listing_props(ctx, id, shop_id, prop_id, query, out, format, transform, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
        result = 1
    return result
