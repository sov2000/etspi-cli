import click

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes

def delete_listing_video(ctx: Any, id: int, shop_id: int, vid_id: int, yes: bool, silent: bool) -> None:
    ctx.vlog(f"Delete Action for Listing ID: {id} and Video ID: {vid_id}")
    etsy = ctx.get_etsy("VIDEO-DELETE")
    confirm = True
    if not yes:
        user_input = input(f"Are you sure you want to delete video {vid_id} from listing {id}? (yes/no):")
        if user_input.lower() not in ['yes', 'y']:
            confirm = False 
    if confirm:
        ctx.vlog(f"Deleting Video ID: {vid_id} from Listing ID: {id}")
        res = etsy.delete_listing_video(shop_id, id, vid_id)
        if not silent:
            print(res)
    else:
        ctx.vlog(f"Abort Delete Video ID: {vid_id} from Listing ID: {id}")
    return

@click.command("video-delete", short_help="Delete listing video by Video and Listing ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("-s", "--shop-id", required=False, type=click.INT, help="Shop ID to use for video delete action.")
@click.option("-vi", "--vid-id", required=True, type=click.INT, help="Video ID to delete.")
@click.option("-Y", "--yes", required=False, default=False, is_flag=True, help="Do not ask to confirm video delete.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Suppress console output.")
@pass_environment
def cli(ctx, id, shop_id, vid_id, yes, silent):
    """Perform a Delete action on a listing by Listing and Video IDs."""
    ctx.check_auth("VIDEO-DELETE")
    if not id is None:
        ctx.vlog(f"Process DELETE VIDEO listing: {id}")
    try:
        delete_listing_video(ctx, id, shop_id, vid_id, yes, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
