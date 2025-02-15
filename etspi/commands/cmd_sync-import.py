import click
import os

from typing import Any, Dict, List, Optional
from rich import print
from etspi.util import sync, listfileio, pprint
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes, ListingState, SortOn, SortOrder
from etspi.etsyv3.models import CreateDraftListingRequest, UpdateListingRequest

def import_listing(ctx: Any, id: int, out: Any, root: str, format: str, with_folder: bool = False) -> Dict:
    etsy = ctx.get_etsy("SYNC-IMPORT")
    res = etsy.get_listing(id, [Includes.SHIPPING, Includes.IMAGES])
    res = UpdateListingRequest.generate_request_from_listing_response(res).get_dict()
    listing = sync.Listing(id, res)
    if "image_ids" in res:
        listing.images = res["image_ids"]
        del res["image_ids"]
    if not out:
        if with_folder:
            fld_path = os.path.join(root, str(id))
            if not os.path.exists(fld_path):
                os.makedirs(fld_path)
        file_ext = "ejs" if format == "JSON" else "eyml"
        filename = os.path.join(root, os.path.join(str(id), f"{id}.{file_ext}") if with_folder else f"{id}.{file_ext}")
        listfileio.save_listing_file(ctx, listing.to_dict(), filename, format)
    else:
        listfileio.save_listing_file(ctx, listing.to_dict(), None, format, out)
    return listing

def sync_listing(ctx: Any, id: int, out: Any, root: str, format: str) -> None:
    ctx.vlog(f"Sync Action for Listing ID: {id}")
    try:
        if id:
            import_listing(ctx, id, out, root, format, False)
            ctx.vlog(f"Successfully synced listing ID: {id}")
        else:
            raise Exception("Listing ID is not valid")
    except Exception as ex:
        ctx.log(f"Error processing import listing ID: {id} - {ex}")
    return

def sync_shop_section(ctx: Any, shop_id: int, section_id: List, state: str, root: str, format: str) -> None:
    ctx.vlog(f"Sync Action for Shop ID: {shop_id} Section ID: {section_id}")
    try:
        listing_count = 0
        offset = 0
        listing_set = []
        etsy = ctx.get_etsy("SYNC-IMPORT")
        if shop_id:
            while True:
                if shop_id and section_id:
                    res = etsy.get_listings_by_shop_section_id(shop_id, section_id, 100, offset, SortOn.CREATED, SortOrder.DESC)
                else:
                    res = etsy.get_listings_by_shop(shop_id, state, 100, offset, SortOn.CREATED, SortOrder.DESC, None)
                if res:
                    listing_count = res["count"]
                    r = [x["listing_id"] for x in res["results"]]
                    listing_set.extend(r)
                    offset += 100
                else:
                    break
                if offset >= listing_count:
                    break
            if listing_set:
                ok_count = 0
                for l in listing_set:
                    try:
                        import_listing(ctx, l, None, root, format, with_folder = True)
                        ctx.vlog(f"Successfully synced listing ID: {l}")
                        ok_count += 1
                    except Exception as ex:
                        ctx.log(f"Error processing import listing ID: {l} - {ex}")
                ctx.vlog(pprint.context_pprint(f"Successfully synced [green]{ok_count}[/green] out of [magenta]{len(listing_set)}[/magenta] listings for Shop ID: {shop_id} Section ID: {section_id}"))
        else:
            raise Exception("Shop ID is not valid")
    except Exception as ex:
        ctx.log(f"Error processing import for shop ID: {shop_id} section ID: {section_id} - {ex}")
    return

@click.command("sync-import", short_help="Import listings by ID, Section, or Shop for future sync commands.")
@click.option("-i", "--id", required=False, type=click.INT, help="Listing ID to which apply action.")
@click.option("-si", "--section-id", required=False, type=click.INT, default=None, help="Shop Section ID for which to retrieve listings.", multiple=True)
@click.option("-s", "--shop-id", required=False, type=click.INT, default=0, help="Shop ID for which to retrieve listings.")
@click.option("-st", "--state", required=False, default=ListingState.ACTIVE.value, type=click.Choice([ListingState.ACTIVE.value, ListingState.INACTIVE.value, ListingState.SOLD_OUT.value, ListingState.DRAFT.value, ListingState.EXPIRED.value], case_sensitive=False), multiple=False)
@click.option("-o", "--out", required=False, type=click.File(mode="w", encoding="utf-8", errors="strict", lazy=None, atomic=False), help="Output result into specified file")
@click.option("-R", "--root-folder", required=False, type=click.STRING, default=".", help="Set root folder for import operation.")
@click.option("-F", "--format", required=False, default="JSON", type=click.Choice(["JSON", "YAML"], case_sensitive=False), multiple=False, help="Set export listing format to JSON or YAML.")
#@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, id, section_id, shop_id, state, out, root_folder, format) -> int:
    """Perform a IMPORT action on a listing, shop section, or shop by IDs."""
    result = 0
    ctx.check_auth("SYNC-IMPORT")
    try:
        ctx.vlog(f"Process SYNC-IMPORT")
        sts = ListingState(state) if state else None
        if shop_id and section_id:
            sync_shop_section(ctx, shop_id, section_id, sts, root_folder, format)
        elif shop_id:
            sync_shop_section(ctx, shop_id, None, sts, root_folder, format)
        elif id:
            sync_listing(ctx, id, out, root_folder, format)
        else:
            raise Exception("No valid options provided for import")
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
        result = 1
    return result
