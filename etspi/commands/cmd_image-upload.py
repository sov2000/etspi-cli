import click

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes
from etspi.etsyv3.models import UploadListingImageRequest, UpdateListingImageIDRequest

def upload_listing_image(ctx: Any, id: int, shop_id: int, src_file: Any, img_id: int, rank: int,
                        overwrite: bool, watermark: bool, alt_text: str, silent: bool) -> None:
    ctx.vlog(f"Upload or Update Image Action for Listing ID: {id} Image ID {img_id}")
    etsy = ctx.get_etsy("LISTING-UPDATE")
    if not src_file is None:
        img_content = src_file.read()
        listing_img = UploadListingImageRequest(image_bytes=img_content, listing_image_id=img_id, rank=rank, overwrite=overwrite, 
                                                is_watermarked=watermark, alt_text=alt_text)
    elif not img_id is None:
        listing_img = UpdateListingImageIDRequest(listing_image_id=img_id, rank=rank, overwrite=overwrite,
                                                is_watermarked=watermark, alt_text=alt_text)
    else:
        raise click.BadArgumentUsage("No Source File or Image Id provided for upload or update.")
    res = etsy.update_listing_image_id(shop_id, id, listing_img) 
    if not silent:
        print(res)
    return

@click.command("image-upload", short_help="Upload a new listing image or update by Image ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("-s", "--shop-id", required=True, type=click.INT, help="Shop ID to use for update and other actions.")
@click.option("-f", "--src-file", required=False, help="Source image file from which to read content to upload.",
              type=click.File(mode="rb", encoding="utf-8", errors="strict", lazy=None, atomic=False))
@click.option("-ii", "--img-id", required=False, default=1, type=click.INT, help="Image ID to update for existing.")
@click.option("-r", "--rank", required=False, default=1, type=click.INT, help="Image rank to upload or update.")
@click.option("-O", "--overwrite", required=False, default=False, is_flag=True, help="Overwrite file flag to replace existing image.")
@click.option("-W", "--watermark", required=False, default=False, is_flag=True, help="Set to indicate image has a watermark.")
@click.option("-a", "--alt-text", required=False, default="", type=click.STRING, help="Image ALT Text to set upon upload or update.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, id, shop_id, src_file, img_id, rank, overwrite, watermark, alt_text, silent):
    """Upload a new image or Update existing image by Listing ID and Image ID."""
    ctx.check_auth("IMAGE-UPLOAD")
    if not id is None:
        ctx.vlog(f"Process Upload or Update Image Listing ID: {id} Image ID: {img_id}")
    try:
        upload_listing_image(ctx, id, shop_id, src_file, img_id, rank, overwrite, watermark, alt_text, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
