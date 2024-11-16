import datetime
import os
import time
import json
import click
import jmespath
import rich.box

from typing import Any, Dict, List, Optional
from rich import print
from rich.console import Console
from rich.panel import Panel
from etspi.cli import pass_environment, Environment
from etsyv3 import EtsyAPI, Includes
from etsyv3.models import CreateDraftListingRequest, UpdateListingInventoryRequest

def get_listing(ctx: Any, id: str, includes: List, transform: bool, query: str, out: Any, silent: str) -> None:
    ctx.vlog(f"Get Action for Listing ID: {id}")
    etsy = ctx.get_etsy("LISTING")
    res = etsy.get_listing(id, includes)
    if transform:
        res = CreateDraftListingRequest.generate_request_from_listing_response(res).get_dict()
    if res:
        if query:
            res = jmespath.search(query, res)
        if out:
            out.write(json.dumps(res, indent=4))
        if not silent:
            print(res)
    return

def get_listing_inventory(ctx: Any, id: str, transform: bool, query: str, out: Any, silent: str) -> None:
    ctx.vlog(f"Get Inventroy Action for Listing ID: {id}")
    etsy = ctx.get_etsy("LISTING")
    res = etsy.get_listing_inventory(id)
    if transform:
        res = UpdateListingInventoryRequest.generate_request_from_inventory_response(res).get_dict()
    if res:
        if query:
            res = jmespath.search(query, res)        
        if out:
            out.write(json.dumps(res, indent=4))
        if not silent:
            print(res)
    return

def get_includes_from_str(includes: List) -> List[Includes]:
    incs = [Includes(i) for i in includes]
    return incs

def delete_listing(ctx: Any, id: str, silent: bool) -> None:
    ctx.vlog(f"Delete Action for Listing ID: {id}")
    etsy = ctx.get_etsy("LISTING")
    res = etsy.delete_listing(id)
    if not silent:
        print(res)
    return

@click.command("listing", short_help="Retrieve listing by ID")
@click.argument("action", type=click.Choice(["get", "get-iv", "delete"], case_sensitive=False), default="get")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("-in", "--include", type=click.Choice([Includes.SHIPPING.value, Includes.IMAGES.value, Includes.SHOP.value, Includes.USER.value, Includes.TRANSLATIONS.value, Includes.INVENTORY.value, Includes.VIDEOS.value], case_sensitive=False), multiple=True)
@click.option("-t", "--transform", is_flag=True, default=False, help="Transform listing or inventory response into format suitable for create or update request")
@click.option("-q", "--query", type=click.STRING, help="JMESPath query to filter the output of the command")
@click.option("-o", "--out", required=False, default="-", type=click.File(mode="w", encoding="utf-8", errors="strict", lazy=None, atomic=False), help="Also output result into a file")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output")
@pass_environment
def cli(ctx, action, id, include, transform, query, out, silent):
    """Perform an action on a listing by its ID.\n
    - get:      Get listing data by ID\n
    - delete:   Delete listing by ID\n
    - get-iv:   Get listing inventory data by ID 
    """
    ctx.check_auth("LISTING")
    if not id is None:
        ctx.vlog(f"Process listing: {id}")
    try:
        if action.lower() == "get":
            incs = None
            if include:
                incs = get_includes_from_str(include)
            get_listing(ctx, id, incs, transform, query, out, silent)
        elif action.lower() == "get-iv":
            get_listing_inventory(ctx, id, transform, query, out, silent)
        elif action.lower() == "delete":
            delete_listing(ctx, id, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
