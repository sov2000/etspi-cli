import json
import click
import os

from typing import Any, Dict, List, Optional
from rich import print
from etspi.util import sync, listfileio, pprint
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes, ListingState, SortOn, SortOrder
from etspi.etsyv3.models import CreateDraftListingRequest, UpdateListingRequest

def setup_stage_folder(root: str) -> str:
    directory_path = os.path.join(root, ".etspi_stage")
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    # scan directory_path for all files and subdirectories and remove them all
    dir_items = listfileio.scan_local_root(directory_path, ["*.*"])
    for item in dir_items:
        if os.path.isfile(item):
            os.remove(item)
    # for item in os.listdir(directory_path):
    #     item_path = os.path.join(directory_path, item)
    #     if os.path.isfile(item_path):
    #         os.remove(item_path)
    #     # else:
    #     #     os.rmdir(item_path)
    return directory_path

def get_stage_file(ctx: Any, operation: str, id: int) -> str:
    stage_fldr = os.path.join(ctx.options["stage_fldr"], operation)
    if not os.path.exists(stage_fldr):
        os.makedirs(stage_fldr)
    return os.path.join(stage_fldr, f"{id}.ejs")

def stage_create_listing(ctx: Any, src_file: str, indx: int, shop_id: int, listing: Any) -> sync.SyncOperation:
    stage_file = get_stage_file(ctx, "draft", indx)
    listfileio.save_listing_file(ctx, listing, stage_file)
    return sync.SyncOperation(src_file=src_file, operation="draft", params={
        "shop_id": shop_id, "src_file": stage_file, "listing_id": True, "silent": True
        }).to_dict()

def stage_update_listing(ctx: Any, src_file: str, id: int, shop_id: int, listing: Any) -> sync.SyncOperation:
    stage_file = get_stage_file(ctx, "listing-update", id)
    listfileio.save_listing_file(ctx, listing, stage_file)
    return sync.SyncOperation(src_file=src_file, operation="listing-update", params={
        "id": id, "shop_id": shop_id, "src_file": stage_file, "silent": True
        }).to_dict()

def stage_update_listing_inventory(ctx: Any, src_file: str, id: int, shop_id: int, inventory: Any) -> sync.SyncOperation:
    stage_file = get_stage_file(ctx, "listing-update-iv", id)
    listfileio.save_listing_file(ctx, inventory, stage_file)
    return sync.SyncOperation(src_file=src_file, operation="listing-update-iv", params={
        "id": id, "src_file": stage_file, "silent": True
        }).to_dict()

def stage_update_listing_properties(ctx: Any, src_file: str, id: int, shop_id: int, properties: Any) -> sync.SyncOperation:
    stage_file = get_stage_file(ctx, "prop-update", id)
    listfileio.save_listing_file(ctx, properties, stage_file)
    return sync.SyncOperation(src_file=src_file, operation="prop-update", params={
        "id": id, "shop_id": shop_id, "src_file": stage_file, "silent": True
        }).to_dict()

def plan_listing_sync(ctx: Any, shop_id: int, root: str, fmt_list: List) -> None:
    ctx.vlog(f"Plan Listing Updates for Shop ID: {shop_id}")
    list_ops = []
    listing_files = listfileio.scan_local_root(ctx, root, fmt_list)
    ctx.vlog(f"Found {len(listing_files)} listing files to scan.")
    draft_indx = 0
    for file in listing_files:
        try:
            unchng = True
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
            list_hash = sync.hash_list_data(listing_data)
            if list_hash != listing_meta.get("listing_hash", ""):
                if id:
                    ctx.vlog(pprint.context_pprint(f"[cyan bold]UPDATED[/cyan bold] - Listing {id} in file {file} - [green]queued[/green]"))
                    list_ops.append(stage_update_listing(ctx, file, id, shop_id, listing_data))
                else:
                    ctx.vlog(pprint.context_pprint(f"[green bold]NEW[/green bold] - Listing in file {file} - [green]queued[/green]"))
                    list_ops.append(stage_create_listing(ctx, file, draft_indx, shop_id, listing_data))
                    draft_indx += 1
                unchng = False
            inv_data = listing.get("inventory", None)
            if inv_data and sync.hash_list_data(inv_data) != listing_meta.get("inventory_hash", ""):
                ctx.vlog(pprint.context_pprint(f"[cyan bold]UPDATED[/cyan bold] - Inventory {id} in file {file} - [green]queued[/green]"))
                list_ops.append(stage_update_listing_inventory(ctx, file, id, shop_id, inv_data))
                unchng = False
            prp_data = listing.get("properties", None)
            if prp_data and sync.hash_list_data(prp_data) != listing_meta.get("properties_hash", "") and len(listing_meta.get("properties_item_hashes", [])) == len(prp_data):
                prp_data_chg = [prp for prp, hash in zip(prp_data, listing_meta["properties_item_hashes"]) if sync.hash_list_data(prp) != hash]
                if len(prp_data_chg) > 0:
                    list_ops.append(stage_update_listing_properties(ctx, file, id, shop_id, prp_data_chg))
                    ctx.vlog(pprint.context_pprint(f"[cyan bold]UPDATED[/cyan bold] - Properties {len(prp_data_chg)} items {id} in file {file} - [green]queued[/green]"))
                    unchng = False
            if unchng:
                ctx.vlog(pprint.context_pprint(f"[yellow bold]UNCHANGED[/yellow bold] - Listing {id} in file {file} - [yellow]skipped[/yellow]"))                
        except Exception as ex:
            ctx.log(f"Error processing listing file {file} - {ex}")
            continue
    new_llist_ctn = sum([1 for o in list_ops if o["operation"] == "draft"])
    upd_llist_ctn = sum([1 for o in list_ops if o["operation"] in ["listing-update", "listing-update-iv"]])
    ctx.vlog(pprint.context_pprint(f"Found [green]{new_llist_ctn}[/green] new listings and [yellow]{upd_llist_ctn}[/yellow] listing updates."))
    if len(list_ops) > 0:
        stage_file = os.path.join(ctx.options["stage_fldr"], "plan.json")
        with open(stage_file, "w", encoding="utf-8") as file:
            file.write(json.dumps(list_ops, indent=4))
        ctx.vlog(f"Plan file saved to {stage_file}.")
    else:
        ctx.vlog(f"No listing file changes found to plan for update.")
    return

@click.command("sync-plan", short_help="Search for listing files, detect changes, and plan for listing updates.")
@click.option("-s", "--shop-id", required=True, type=click.INT, default=0, help="Shop ID for which to plan listing updates.")
@click.option("-R", "--root-folder", required=False, type=click.STRING, default=".", help="Set root folder for scan operation.")
@click.option("-F", "--format", required=False, default=None, type=click.Choice(["JSON", "YAML"], case_sensitive=False), multiple=False, help="Set format to JSON or YAML to scan the root folder.")
@pass_environment
def cli(ctx, shop_id, root_folder, format) -> int:
    """Perform a PLAN action on all matching files from root folder."""
    result = 0
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
        plan_listing_sync(ctx, shop_id, root_folder, fmt_list)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
        result = 1
    return result
