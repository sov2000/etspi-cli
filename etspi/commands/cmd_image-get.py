import json
import click
import jmespath

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI

def get_listing_image(ctx: Any, id: str, img_id: str, query: str, out: Any, silent: bool) -> None:
    ctx.vlog(f"Get Image Action for Listing ID: {id} Image ID: {img_id}")
    etsy = ctx.get_etsy("LISTING-GET")
    if img_id > 0:
        res = etsy.get_listing_image(id, img_id)
    else:
        res = etsy.get_listing_images(id)
    if res:
        if query:
            res = jmespath.search(query, res)
        if out:
            out.write(json.dumps(res, indent=4))
        if not silent:
            print(res)
    return

@click.command("image-get", short_help="Retrieve or Get listing image(s) by Image and Listing ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID from which to retrieve the image.")
@click.option("-ii", "--img-id", required=False, default=0, type=click.INT, help="Image ID to retrieve or, if omitted or 0, get all images.")
@click.option("-q", "--query", type=click.STRING, help="JMESPath query to filter the output of the command.")
@click.option("-o", "--out", required=False, type=click.File(mode="w", encoding="utf-8", errors="strict", lazy=None, atomic=False), help="Also output result into a file.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, id, img_id, query, out, silent):
    """Perform a GET IMAGE action on a listing by Listing ID and optional Image ID."""
    ctx.check_auth("IMAGE-GET")
    if not id is None:
        ctx.vlog(f"Process GET Image Listing ID: {id} Image ID: {img_id}")
    try:
        get_listing_image(ctx, id, img_id, query, out, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
