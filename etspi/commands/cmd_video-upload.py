import click
import os

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes
from etspi.etsyv3.models import UploadListingVideoRequest

def upload_listing_video(ctx: Any, id: int, shop_id: int, src_file: Any, vid_id: int, silent: bool) -> None:
    ctx.vlog(f"Upload or Update Video Action for Listing ID: {id} Video ID {vid_id}")
    etsy = ctx.get_etsy("LISTING-UPDATE")
    if not src_file is None:
        vid_content = src_file.read()
        listing_vid = UploadListingVideoRequest(video_bytes=vid_content, listing_video_id=None, name=os.path.basename(src_file.name))
    elif not vid_id is None:
        listing_vid = UploadListingVideoRequest(video_bytes=None, listing_video_id=vid_id, name=str(vid_id))
    else:
        raise click.BadArgumentUsage("No Source File provided for upload or update.")
    res = etsy.upload_listing_video(shop_id, id, listing_vid)
    if not silent:
        print(res)
    return

@click.command("video-upload", short_help="Upload a new listing video or update by Video ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("-s", "--shop-id", required=True, type=click.INT, help="Shop ID to use for update and other actions.")
@click.option("-f", "--src-file", required=False, help="Source video file from which to read content to upload.",
              type=click.File(mode="rb", encoding="utf-8", errors="strict", lazy=None, atomic=False))
@click.option("-vi", "--vid-id", required=False, type=click.INT, help="Video ID to update for existing.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Suppress console output.")
@pass_environment
def cli(ctx, id, shop_id, src_file, vid_id, silent):
    """Upload a new video or Update existing video by Listing ID and Video ID."""
    ctx.check_auth("VIDEO-UPLOAD")
    if not id is None:
        ctx.vlog(f"Process Upload or Update Video Listing ID: {id} Video ID: {vid_id}")
    try:
        upload_listing_video(ctx, id, shop_id, src_file, vid_id, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
