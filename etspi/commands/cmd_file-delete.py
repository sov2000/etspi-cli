import click

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes

def delete_listing_file(ctx: Any, id: int, shop_id: int, file_id: int, yes: bool, silent: bool) -> None:
    ctx.vlog(f"Delete Action for Listing ID: {id} and File ID: {file_id}")
    etsy = ctx.get_etsy("FILE-DELETE")
    confirm = True
    if not yes:
        user_input = input(f"Are you sure you want to delete file {file_id} from listing {id}? (yes/no):")
        if user_input.lower() not in ['yes', 'y']:
            confirm = False 
    if confirm:
        ctx.vlog(f"Deleting File ID: {file_id} from Listing ID: {id}")
        res = etsy.delete_listing_file(shop_id, id, file_id)
        if not silent:
            print(res)
    else:
        ctx.vlog(f"Abort Delete File ID: {file_id} from Listing ID: {id}")
    return

@click.command("file-delete", short_help="Delete listing file by File and Listing ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("-s", "--shop-id", required=False, type=click.INT, help="Shop ID to use for delete action.")
@click.option("-fi", "--file-id", required=True, type=click.INT, help="File ID to delete.")
@click.option("-Y", "--yes", required=False, default=False, is_flag=True, help="Do not ask to confirm file delete.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Suppress console output.")
@pass_environment
def cli(ctx, id, shop_id, file_id, yes, silent):
    """Perform a Delete action on a listing by Listing and File IDs."""
    ctx.check_auth("FILE-DELETE")
    if not id is None:
        ctx.vlog(f"Process DELETE FILE listing: {id}")
    try:
        delete_listing_file(ctx, id, shop_id, file_id, yes, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")