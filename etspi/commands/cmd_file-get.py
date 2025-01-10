import json
import click
import jmespath

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI

def get_listing_file(ctx: Any, id: int, shop_id: int, file_id: int, query: str, out: Any, silent: bool) -> None:
    ctx.vlog(f"Get File Action for Listing ID: {id} File ID: {file_id}")
    etsy = ctx.get_etsy("LISTING-GET")
    if file_id > 0:
        res = etsy.get_listing_file(shop_id, id, file_id)
    else:
        res = etsy.get_all_listing_files(shop_id, id)
    if res:
        if query:
            res = jmespath.search(query, res)
        if out:
            out.write(json.dumps(res, indent=4))
        if not silent:
            print(res)
    return

@click.command("file-get", short_help="Retrieve or Get listing file(s) by File and Listing ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID from which to retrieve the file.")
@click.option("-s", "--shop-id", required=True, type=click.INT, help="Shop ID to use for which to apply the get file(s) actions.")
@click.option("-fi", "--file-id", required=False, default=0, type=click.INT, help="File ID to retrieve or, if omitted or 0, get all files.")
@click.option("-q", "--query", type=click.STRING, help="JMESPath query to filter the output of the command.")
@click.option("-o", "--out", required=False, type=click.File(mode="w", encoding="utf-8", errors="strict", lazy=None, atomic=False), help="Also output result into a file.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Suppress console output.")
@pass_environment
def cli(ctx, id, shop_id, file_id, query, out, silent):
    """Perform a GET FILE action on a listing by Listing ID and optional File ID."""
    ctx.check_auth("FILE-GET")
    if not id is None:
        ctx.vlog(f"Process GET File Listing ID: {id} File ID: {file_id}")
    try:
        get_listing_file(ctx, id, shop_id, file_id, query, out, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")