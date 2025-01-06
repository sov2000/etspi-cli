import json
import click
import jmespath

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes, ListingState, SortOn, SortOrder
from etspi.etsyv3.models import UpdateListingPropertyRequest

def find_shop_listings(ctx: Any, shop_id: int, section_id: List, state: List, keywords: str, range: tuple, sort_on: List, 
                       sort_order: List, include: List, query: str, out: Any, silent: bool) -> None:
    ctx.vlog(f"Find Shop listings by ID: {shop_id}")
    etsy = ctx.get_etsy("SHOP-FIND")
    if shop_id > 0:
        offset, limit = range if range else (None, None)
        if section_id:
            res = etsy.get_listings_by_shop_section_id(shop_id, section_id, limit, offset, sort_on, sort_order)
        elif keywords:
            res = etsy.find_all_active_listings_by_shop(shop_id, limit, sort_on, sort_order, offset, keywords)
        else:
            res = etsy.get_listings_by_shop(shop_id, state, limit, offset, sort_on, sort_order, include)
    else:
        raise click.BadArgumentUsage("No Shop ID provided to find shop listings.") 
    if res:
        if query:
            res = jmespath.search(query, res)
        if out:
            out.write(json.dumps(res, indent=4))
        if not silent:
            print(res)
    return

@click.command("shop-find", short_help="Search Shop Listings by Shop ID")
@click.option("-s", "--shop-id", required=True, type=click.INT, default=0, help="Shop ID for which to retrieve listings.")
@click.option("-si", "--section-id", required=False, type=click.INT, default=None, help="Shop Section ID for which to retrieve listings.", multiple=True)
@click.option("-st", "--state", type=click.Choice([ListingState.ACTIVE.value, ListingState.INACTIVE.value, ListingState.SOLD_OUT.value, ListingState.DRAFT.value, ListingState.EXPIRED.value], case_sensitive=False), multiple=False)
@click.option("-K", "--keywords", required=False, type=click.STRING, help="Keywords to filter the active shop listings.")
@click.option("-R", "--range", required=False, type=click.INT, nargs=2, help="Range of shop listings to display from the search, offset and limit.")
@click.option("-ss", "--sort-on", type=click.Choice([SortOn.CREATED.value, SortOn.PRICE.value, SortOn.UPDATED.value, SortOn.SCORE.value], case_sensitive=False), multiple=False)
@click.option("-so", "--sort-order", type=click.Choice([SortOrder.ASC.value, SortOrder.DESC.value], case_sensitive=False), multiple=False)
@click.option("-in", "--include", type=click.Choice([Includes.SHIPPING.value, Includes.IMAGES.value, Includes.SHOP.value, Includes.USER.value, Includes.TRANSLATIONS.value, Includes.INVENTORY.value, Includes.VIDEOS.value], case_sensitive=False), multiple=True)
@click.option("-q", "--query", required=False, type=click.STRING, help="JMESPath query to filter the output of the command.")
@click.option("-o", "--out", required=False, type=click.File(mode="w", encoding="utf-8", errors="strict", lazy=None, atomic=False), help="Also output result into a file")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, shop_id, section_id, state, keywords, range, sort_on, sort_order, include, query, out, silent):
    """Perform a FIND Shop listings action by Shop ID."""
    ctx.check_auth("SHOP-FIND")
    if not shop_id is None:
        ctx.vlog(f"Process FIND shop listings: {shop_id}")
    try:
        incs = [Includes(i) for i in include] if include else None
        sts = ListingState(state) if state else None
        sos = SortOn(sort_on) if sort_on else None
        sors = SortOrder(sort_order) if sort_order else None
        find_shop_listings(ctx, shop_id, section_id, sts, keywords, range, sos, sors, incs, query, out, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
