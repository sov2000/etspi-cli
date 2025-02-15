import click

from typing import Any, Dict, List, Optional
from rich import print
from etspi.util import sync, listfileio, pprint
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes, ListingState, SortOn, SortOrder
from etspi.etsyv3.models import CreateDraftListingRequest, UpdateListingRequest

def import_listing(ctx: Any, id: int, file: str) -> Dict:
    etsy = ctx.get_etsy("SYNC-IMPORT")
    res = etsy.get_listing(id, [Includes.SHIPPING, Includes.IMAGES])
    res = UpdateListingRequest.generate_request_from_listing_response(res).get_dict()
    listing = sync.Listing(id, res)
    if "image_ids" in res:
        listing.images = res["image_ids"]
        del res["image_ids"]
    format = "JSON" if file.endswith(".ejs") else "YAML"
    listfileio.save_listing_file(ctx, listing.to_dict(), file, format)
    return listing

def pull_listing_sync(ctx: Any, root: str, fmt_list: List) -> None:
    ctx.vlog(f"Pull Listing Updates from Remote for Root: {root}")
    listing_files = listfileio.scan_local_root(ctx, root, fmt_list)
    ctx.vlog(f"Found {len(listing_files)} listing files to pull updates.")
    success_ctn = 0
    for file in listing_files:
        try:
            listing = listfileio.load_listing_file(ctx, file)
            if listing:
                listing_meta = listing.get("meta", {})
                if listing_meta:
                    id = listing_meta.get("listing_id", 0)
                    if id:
                        import_listing(ctx, id, file)
                        ctx.vlog(f"Listing ID: {id} in {file} updated from remote.")
                        success_ctn += 1
                    else:
                        raise Exception(f"Listing ID is not valid in file {file}")
        except Exception as ex:
            ctx.log(f"Error processing listing file {file} - {ex}")
            continue
    ctx.vlog(pprint.context_pprint(f"Updated [green]{success_ctn}[/green] ouf of [magenta]{len(listing_files)}[/magenta] listing files from remote."))
    return

@click.command("sync-pull", short_help="Search for local listing files and update from remote listing.")
@click.option("-R", "--root-folder", required=False, type=click.STRING, default=".", help="Set root folder for scan operation.")
@click.option("-F", "--format", required=False, default=None, type=click.Choice(["JSON", "YAML"], case_sensitive=False), multiple=False, help="Set format to JSON or YAML to scan the root folder.")
@pass_environment
def cli(ctx, root_folder, format) -> int:
    """Perform a PULL action on all matching files from root folder."""
    result = 0
    ctx.check_auth("SYNC-PULL")
    ctx.vlog(f"Process SYNC-PULL root folder: {root_folder}")
    try:
        fmt_list = []
        if format == "JSON":
            fmt_list = ["*.ejs"]
        elif format == "YAML":
            fmt_list = ["*.eyml"]
        else:
            fmt_list = ["*.ejs", "*.eyml"]
        pull_listing_sync(ctx, root_folder, fmt_list)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
        result = 1
    return result
