import click

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etsyv3 import EtsyAPI, Includes

def delete_listing(ctx: Any, id: str, silent: bool) -> None:
    ctx.vlog(f"Delete Action for Listing ID: {id}")
    etsy = ctx.get_etsy("LISTING-DELETE")
    res = etsy.delete_listing(id)
    if not silent:
        print(res)
    return

@click.command("listing-delete", short_help="Delete a listing by ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, id, silent):
    """Perform a Delete action on a listing by its ID."""
    ctx.check_auth("LISTING-DELETE")
    if not id is None:
        ctx.vlog(f"Process DELETE listing: {id}")
    try:
        delete_listing(ctx, id, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
