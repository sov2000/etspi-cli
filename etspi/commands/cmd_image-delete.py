import click

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes

def delete_listing_image(ctx: Any, id: str, shop_id: str, img_id: str, yes: bool, silent: bool) -> None:
    ctx.vlog(f"Delete Action for Listing ID: {id} and Image ID: {img_id}")
    etsy = ctx.get_etsy("IMAGE-DELETE")
    confirm = True
    if not yes:
        user_input = input(f"Are you sure you want to delete image {img_id} from listing {id}? (yes/no):")
        if user_input.lower() not in ['yes', 'y']:
            confirm = False 
    if confirm:
        ctx.vlog(f"Deleting Image ID: {img_id} from Listing ID: {id}")
        res = etsy.delete_listing_image(shop_id, id, img_id)
        if not silent:
            print(res)
    else:
        ctx.vlog(f"Abort Delete Image ID: {img_id} from Listing ID: {id}")
    return

@click.command("image-delete", short_help="Delete listing image by Image and Listing ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("-s", "--shop-id", required=False, type=click.INT, help="Shop ID to use for update and other actions.")
@click.option("-ii", "--img-id", required=True, type=click.INT, help="Image ID to delete.")
@click.option("-Y", "--yes", required=False, default=False, is_flag=True, help="Do not ask to confirm image delete.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, id, shop_id, img_id, yes, silent):
    """Perform a Delete action on a listing by Listing and Image IDs."""
    ctx.check_auth("IMAGE-DELETE")
    if not id is None:
        ctx.vlog(f"Process DELETE IMAGE listing: {id}")
    try:
        delete_listing_image(ctx, id, shop_id, img_id, yes, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
