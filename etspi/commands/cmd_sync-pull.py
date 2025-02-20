import click

from typing import Any, Dict, List, Optional
from rich import print
from etspi.util import sync, listfileio, pprint
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes, ListingState, SortOn, SortOrder
from etspi.etsyv3.models import CreateDraftListingRequest, UpdateListingRequest, UpdateListingInventoryRequest, UpdateListingPropertyRequest

def import_listing(ctx: Any, shop_id: int, id: int, file: str) -> Dict:
    etsy = ctx.get_etsy("SYNC-IMPORT")
    res = etsy.get_listing(id, [Includes.SHIPPING, Includes.IMAGES, Includes.INVENTORY])
    prp = etsy.get_listing_properties(shop_id, id)
    lst = UpdateListingRequest.generate_request_from_listing_response(res).get_dict()
    listing = sync.Listing(id, lst)
    if "images" in res:
        lst_imgs = []
        res_imgs = res.get("images", [])
        for img in res_imgs:
            lst_imgs.append(sync.ListingImageRequest.generate_request_from_image_response(img).get_dict())
        listing.images = lst_imgs
    if "inventory" in res:
        inv = UpdateListingInventoryRequest.generate_request_from_inventory_response(res["inventory"]).get_dict()
        listing.inventory = inv
    if prp:
        listing.properties = [UpdateListingPropertyRequest.generate_request_from_listing_property_response(r, r["property_id"]).get_dict() for r in prp['results']]
    format = "JSON" if file.endswith(".ejs") else "YAML"
    listfileio.save_listing_file(ctx, listing.to_dict(), file, format)
    return listing

def check_listing_for_changes(ctx: Any, listing: Dict) -> bool:
    if listing:
        listing_meta = listing.get("meta", {})
        listing_data = listing.get("listing", None)
        if listing_data and sync.hash_list_data(listing_data) != listing_meta.get("listing_hash", ""):
            return True
        inv_data = listing.get("inventory", None)
        if inv_data and sync.hash_list_data(inv_data) != listing_meta.get("inventory_hash", ""):
            return True
        img_data = listing.get("images", None)
        if img_data and sync.hash_list_data(img_data) != listing_meta.get("images_hash", ""):
            return True
        prp_data = listing.get("properties", None)
        if prp_data and sync.hash_list_data(prp_data) != listing_meta.get("properties_hash", ""):
            return True
    return False

def pull_listing_sync(ctx: Any, shop_id: int, root: str, fmt_list: List, changed: bool) -> None:
    ctx.vlog(f"Pull Listing Updates from Remote for Root: {root}")
    listing_files = listfileio.scan_local_root(ctx, root, fmt_list)
    ctx.vlog(f"Found {len(listing_files)} listing files to pull updates.")
    success_ctn = 0
    for file in listing_files:
        try:
            success_ctn += process_listing_file(ctx, shop_id, file, changed)
        except Exception as ex:
            ctx.log(f"Error processing listing file {file} - {ex}")
            continue    
    ctx.vlog(pprint.context_pprint(f"Updated [green]{success_ctn}[/green] out of [magenta]{len(listing_files)}[/magenta] listing files from remote."))
    return

def process_listing_file(ctx: Any, shop_id: int, file: str, changed: bool) -> int:
    listing = listfileio.load_listing_file(ctx, file)
    if not listing:
        raise Exception(f"Invalid listing file {file}")
    listing_data = listing.get("listing", None)
    if not listing_data:
        raise Exception(f"Missing listing data in file {file}")
    listing_meta = listing.get("meta", None)
    if not listing_meta:
        raise Exception(f"Missing meta data in file {file}")
    id = listing_meta.get("listing_id", 0)
    if not id:
        raise Exception(f"Listing ID is not valid in file {file}")
    if changed:
        list_chg = check_listing_for_changes(ctx, listing)
        if list_chg:
            import_listing(ctx, shop_id, id, file)
            ctx.vlog(pprint.context_pprint(f"[green bold]PULLED[/green bold] - Listing ID: {id} in {file} updated from remote."))
            return 1
        else:
            ctx.vlog(pprint.context_pprint(f"[yellow bold]UNCHANGED[/yellow bold] - Listing ID: {id} in {file} skipped."))
    else:
        import_listing(ctx, shop_id, id, file)
        ctx.vlog(pprint.context_pprint(f"[green bold]PULLED[/green bold] - Listing ID: {id} in {file} updated from remote."))
        return 1
    return 0

@click.command("sync-pull", short_help="Search for local listing files and update from remote listing.")
@click.option("-s", "--shop-id", required=True, type=click.INT, help="Shop ID for which to retrieve listings.")
@click.option("-R", "--root-folder", required=False, type=click.STRING, default=".", help="Set root folder for scan operation.")
@click.option("-F", "--format", required=False, default=None, type=click.Choice(["JSON", "YAML"], case_sensitive=False), multiple=False, help="Set format to JSON or YAML to scan the root folder.")
@click.option("-C", "--changed", required=False, default=False, is_flag=True, help="Only sync pull local updated/changed files.")
@pass_environment
def cli(ctx, shop_id, root_folder, format, changed) -> int:
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
        pull_listing_sync(ctx, shop_id, root_folder, fmt_list, changed)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
        result = 1
    return result
