import json
import click
import jmespath

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes
from etspi.etsyv3.models import UpdateListingPropertyRequest

def get_shop_info(ctx: Any, shop_id: int, user_id: int, name: str, range: tuple, query: str, out: Any, silent: bool) -> None:
    ctx.vlog(f"Get Shop information by ID: {shop_id}")
    etsy = ctx.get_etsy("SHOP-GET")
    if shop_id > 0:
        res = etsy.get_shop(shop_id)
    elif user_id > 0:
        res = etsy.get_shop_by_owner_user_id(user_id)
    elif name:
        if range:
            res = etsy.find_shops(name, range[1], range[0])
        else:
            res = etsy.find_shops(name)
    else:
        raise click.BadArgumentUsage("No Shop ID or User Id provided to retrieve shop info.") 
    if res:
        if query:
            res = jmespath.search(query, res)
        if out:
            out.write(json.dumps(res, indent=4))
        if not silent:
            print(res)
    return

@click.command("shop-get", short_help="Retrieve or Get Shop information by Shop ID")
@click.option("-s", "--shop-id", required=False, type=click.INT, default=0, help="Shop ID for which to retrieve shop info.")
@click.option("-u", "--user-id", required=False, type=click.INT, default=0, help="User ID for which to retrieve shop info.")
@click.option("-n", "--name", required=False, type=click.STRING, default=None, help="Shop Name for which to retrieve shop info.")
@click.option("-R", "--range", required=False, type=click.INT, nargs=2, help="Range of shop records to display from the name search, offset and limit.")
@click.option("-q", "--query", type=click.STRING, help="JMESPath query to filter the output of the command.")
@click.option("-o", "--out", required=False, type=click.File(mode="w", encoding="utf-8", errors="strict", lazy=None, atomic=False), help="Also output result into a file")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, shop_id, user_id, name, range, query, out, silent):
    """Perform a GET Shop action by Shop or User ID."""
    ctx.check_auth("SHOP-GET")
    if not shop_id is None:
        ctx.vlog(f"Process GET shop info: {shop_id}")
    try:
        get_shop_info(ctx, shop_id, user_id, name, range, query, out, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
