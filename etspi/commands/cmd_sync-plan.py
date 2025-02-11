import json
import yaml
import click
import jmespath
import hashlib
import time
import os

from typing import Any, Dict, List, Optional
from rich import print
from etspi.util import sync #hash_list_data
from etspi.util import listfileio #scan_local_root, load_listing_file
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes, ListingState, SortOn, SortOrder
from etspi.etsyv3.models import CreateDraftListingRequest, UpdateListingRequest

def setup_stage_folder(root: str) -> str:
    directory_path = os.path.join(root, ".etspi_stage")
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    # scan directory_path for all files and subdirectories and remove them all
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        else:
            os.rmdir(item_path)
    return directory_path

def get_stage_file(ctx: Any, operation: str, id: int) -> str:
    stage_fldr = os.path.join(ctx.options["stage_fldr"], operation)
    if not os.path.exists(stage_fldr):
        os.makedirs(stage_fldr)
    return os.path.join(stage_fldr, f"{id}.json")

def stage_create_listing(ctx: Any, indx: int, shop_id: int, listing: Any) -> sync.SyncOperation:
    stage_file = get_stage_file(ctx, "draft", indx)
    listfileio.save_listing_file(ctx, listing, stage_file)
    return sync.SyncOperation(src_file=stage_file, operation="draft", params={
        "shop_id": shop_id, "src_file": stage_file, "silent": True
        })

def stage_update_listing(ctx: Any, id: int, shop_id: int, listing: Any) -> sync.SyncOperation:
    stage_file = get_stage_file(ctx, "update", id)
    listfileio.save_listing_file(ctx, listing, stage_file)
    return sync.SyncOperation(src_file=stage_file, operation="listing-update", params={
        "id": id, "shop_id": shop_id, "src_file": stage_file, "silent": True
        })

def plan_listing_updates(ctx: Any, shop_id: int, root: str, fmt_list: List) -> None:
    ctx.vlog(f"Plan Listing Updates for Shop ID: {shop_id}")
    list_ops = []
    listing_files = listfileio.scan_local_root(ctx, root, fmt_list)
    ctx.vlog(f"Found {len(listing_files)} listing files to scan.")
    draft_indx = 0
    for file in listing_files:
        try:
            listing = listfileio.load_listing_file(ctx, file)
            if listing:
                listing_data = listing.get("listing", {})
                listing_meta = listing.get("meta", {})
                if listing_meta:
                    id = listing_meta.get("listing_id", 0)
                    if id:
                        list_hash = sync.hash_list_data(listing_data)
                        if list_hash != listing_meta.get("listing_hash", ""):
                            ctx.vlog(f"UPDATED - Listing {id} found in file {file} queued for update.")
                            list_ops.append(stage_update_listing(ctx, id, shop_id, listing, id))
                        else:
                            ctx.vlog(f"UNCHANGED - Listing {id} found in file {file} skipped.")
                    else:
                        ctx.vlog(f"NEW - Listing found in file {file} queued for creation.")
                        list_ops.append(stage_create_listing(ctx, shop_id, listing, draft_indx))
                        draft_indx += 1
        except Exception as ex:
            ctx.log(f"Error processing listing file {file} - {ex}")
            continue
    new_llist_ctn = sum([1 for o in list_ops if o.operation == "draft"])
    upd_llist_ctn = sum([1 for o in list_ops if o.operation == "listing-update"])
    ctx.vlog(f"Found {len(new_llist_ctn)} new listings and {len(upd_llist_ctn)} listings to update.")
    stage_file = os.join(ctx.options["stage_fldr"], "plan.json")
    with open(stage_file, "w", encoding="utf-8") as file:
        file.write(json.dumps(list_ops, indent=4))
    ctx.vlog(f"Plan file saved to {stage_file}.")
    return

@click.command("sync-plan", short_help="Search for listing files, detect changes, and plan for listing updates.")
@click.option("-s", "--shop-id", required=True, type=click.INT, default=0, help="Shop ID for which to plan listing updates.")
@click.option("-R", "--root-folder", required=False, type=click.STRING, default=".", help="Set root folder for scan operation.")
@click.option("-F", "--format", required=False, default=None, type=click.Choice(["JSON", "YAML"], case_sensitive=False), multiple=False, help="Set format to JSON or YAML to scan the root folder.")
@pass_environment
def cli(ctx, shop_id, root_folder, format):
    """Perform a PLAN action on all matching files from root folder."""
    ctx.check_auth("SYNC-PLAN")
    ctx.vlog(f"Process SYNC-PLAN shop ID: {shop_id} root folder: {root_folder}")
    try:
        fmt_list = []
        ctx.options["stage_fldr"] = setup_stage_folder(root_folder)
        if format == "JSON":
            fmt_list = ["*.ejs"]
        elif format == "YAML":
            fmt_list = ["*.eyml"]
        else:
            fmt_list = ["*.ejs", "*.eyml"]
        plan_listing_updates(ctx, shop_id, root_folder, fmt_list)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
