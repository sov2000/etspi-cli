import click
import os

from typing import Any, Dict, List, Optional
from rich import print
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes
from etspi.etsyv3.models import UploadListingFileRequest

def upload_listing_file(ctx: Any, id: int, shop_id: int, src_file: Any, file_id: Optional[int], rank: int, silent: bool) -> None:
    ctx.vlog(f"Upload or Update File Action for Listing ID: {id} File ID {file_id}")
    etsy = ctx.get_etsy("LISTING-UPDATE")
    if src_file is not None:
        file_content = src_file.read()
        listing_file = UploadListingFileRequest(file_bytes=file_content, listing_file_id=None, rank=rank, name=os.path.basename(src_file.name))
    elif not file_id is None:
        listing_file = UploadListingFileRequest(file_bytes=None, listing_file_id=file_id, rank=rank, name=str(file_id))
    else:
        raise click.BadArgumentUsage("No Source File provided for upload or update.")
    res = etsy.upload_listing_file(shop_id, id, listing_file)
    if not silent:
        print(res)
    return

@click.command("file-upload", short_help="Upload a new listing file or update by File ID")
@click.option("-i", "--id", required=True, type=click.INT, help="Listing ID to which apply action.")
@click.option("-s", "--shop-id", required=True, type=click.INT, help="Shop ID to use for update and other actions.")
@click.option("-f", "--src-file", required=False, help="Source file from which to read content to upload.",
              type=click.File(mode="rb", encoding="utf-8", errors="strict", lazy=None, atomic=False))
@click.option("-fi", "--file-id", required=False, type=click.INT, default=1, help="File ID to update for existing.")
@click.option("-r", "--rank", required=False, default=1, type=click.INT, help="File rank to upload or update.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Suppress console output.")
@pass_environment
def cli(ctx, id, shop_id, src_file, file_id, rank, silent):
    """Upload a new file or Update existing file by Listing ID and File ID."""
    ctx.check_auth("FILE-UPLOAD")
    if id is not None:
        ctx.vlog(f"Process Upload or Update File Listing ID: {id} File ID: {file_id}")
    try:
        upload_listing_file(ctx, id, shop_id, src_file, file_id, rank, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")