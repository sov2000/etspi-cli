import json
import click
import jmespath

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI

def get_listing_video(ctx: Any, id: int, vid_id: int, query: str, out: Any, silent: bool) -> None:
    ctx.vlog(f"Get Video Action for Listing ID: {id} Video ID: {vid_id}")
    etsy = ctx.get_etsy("LISTING-GET")
    if vid_id > 0:
        res = etsy.get_listing_video(id, vid_id)
    else:
        res = etsy.get_listing_videos(id)
    if res:
        if query:
            res = jmespath.search(query, res)
        if out:
            out.write(json.dumps(res, indent=4))
        if not silent:
            print(res)
    return

@click.command("video-get", short_help="Retrieve or Get listing video(s) by Video and Listing ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID from which to retrieve the video.")
@click.option("-vi", "--vid-id", required=False, default=0, type=click.INT, help="Video ID to retrieve or, if omitted or 0, get all videos.")
@click.option("-q", "--query", type=click.STRING, help="JMESPath query to filter the output of the command.")
@click.option("-o", "--out", required=False, type=click.File(mode="w", encoding="utf-8", errors="strict", lazy=None, atomic=False), help="Also output result into a file.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Suppress console output.")
@pass_environment
def cli(ctx, id, vid_id, query, out, silent):
    """Perform a GET VIDEO action on a listing by Listing ID and optional Video ID."""
    ctx.check_auth("VIDEO-GET")
    if not id is None:
        ctx.vlog(f"Process GET Video Listing ID: {id} Video ID: {vid_id}")
    try:
        get_listing_video(ctx, id, vid_id, query, out, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")