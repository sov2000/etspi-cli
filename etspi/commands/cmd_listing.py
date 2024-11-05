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

def get_listing(ctx: Any, id: str, includes: List, query: str) -> None:
    ctx.vlog(f"Get Action for Listing ID: {id}")
    etsy = ctx.get_etsy("LISTING")
    #print(etsy.get_listing_inventory(id))
    res = etsy.get_listing(id, includes)
    if res:
        if query:
            print(jmespath.search(query, res))
        else:
            print(res)
    return

def get_includes_from_str(includes: List) -> List[Includes]:
    incs = []
    for i in includes:
        for ii in Includes:
            if i == ii.value:
                incs.append(ii)
    return incs

@click.command("listing", short_help="Retrieve listing by ID")
@click.argument("action", type=click.Choice(["get", "update", "delete"], case_sensitive=False), default="get")
@click.option("-i", "--id", required=True, type=click.STRING, help="Listing ID to which apply action.")
@click.option("-in", "--include", type=click.Choice([Includes.SHIPPING.value, Includes.IMAGES.value, Includes.SHOP.value, Includes.USER.value, Includes.TRANSLATIONS.value, Includes.INVENTORY.value, Includes.VIDEOS.value], case_sensitive=False), multiple=True)
@click.option("-q", "--query", type=click.STRING, help="JMESPath query to filter the output of the command")
@pass_environment
def cli(ctx, action, id, include, query):
    """Perform an action on a listing by its ID."""
    ctx.check_auth("LISTING")
    if not id is None:
        ctx.vlog(f"Process listing: {id}")
    if action == "get":
        incs = None
        if include:
            incs = get_includes_from_str(include)
        get_listing(ctx, id, incs, query)
