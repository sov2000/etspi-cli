import json
import click
import jmespath

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI

def get_listing_image(ctx: Any, user_id: int, query: str, out: Any, silent: bool) -> None:
    ctx.vlog(f"Get User Action for User ID: {user_id}")
    etsy = ctx.get_etsy("USER-GET")
    if user_id > 0:
        res = etsy.get_user(user_id)
    else:
        res = etsy.get_authenticated_user()
    if res:
        if query:
            res = jmespath.search(query, res)
        if out:
            out.write(json.dumps(res, indent=4))
        if not silent:
            print(res)
    return

@click.command("user", short_help="Get User info ID and Shop ID for authorized user.")
@click.option("-u", "--user-id", required=False, type=click.INT, default=0, help="User ID for which to retrieve info.")
@click.option("-q", "--query", type=click.STRING, help="JMESPath query to filter the output of the command.")
@click.option("-o", "--out", required=False, type=click.File(mode="w", encoding="utf-8", errors="strict", lazy=None, atomic=False), help="Also output result into a file.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, user_id, query, out, silent):
    """Perform a GET USER action by User ID or Self."""
    ctx.check_auth("USER-GET")
    if not user_id is None:
        ctx.vlog(f"Process GET User ID: {user_id}")
    try:
        get_listing_image(ctx, user_id, query, out, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
