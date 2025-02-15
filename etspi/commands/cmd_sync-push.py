import json
import click
import os

from typing import Any, Dict, List, Optional
from rich import print
from rich.console import Group, Console
from rich.panel import Panel
from rich.table import Table
from rich.padding import Padding
from etspi.util import sync, listfileio, pprint
from etspi.cli import pass_environment, Environment
from etspi.etsyv3 import EtsyAPI, Includes, ListingState, SortOn, SortOrder
from etspi.etsyv3.models import CreateDraftListingRequest, UpdateListingRequest

def get_operations_from_plan(ctx: Any, root: str) -> List:
    stage_file = os.path.join(root, ".etspi_stage", "plan.json")
    if not os.path.exists(stage_file):
        raise Exception("No Plan File found to process in the root location.")
    ctx.vlog(f"Loading Plan File: {stage_file}")
    with open(stage_file, 'r', encoding='utf-8') as file:
        plan_data = json.load(file)
    return plan_data

def push_preview_listing_sync(ctx: Any, list_ops: List) -> bool:
    confirm = False
    if list_ops and len(list_ops) > 0:
        ctx.vlog(f"Preview Listing Updates from Plan")
        print("="*80)
        for op in list_ops:
            print(f"[yellow bold]FILE:[/yellow bold] {op['src_file']} [red bold]=>[/red bold] [yellow bold]OPS:[/yellow bold] [magenta bold]{op['operation']}[/magenta bold] - [yellow bold]PARAMS:[/yellow bold] {op['params']}")
        operation_counts = {}
        for op in list_ops:
            operation = op['operation']
            if operation in operation_counts:
                operation_counts[operation] += 1
            else:
                operation_counts[operation] = 1
        console = Console()
        table = Table(title="Operations Summary", show_header=True, header_style="bold green")
        table.add_column("Operation Type", justify="left", style="magenta bold")
        table.add_column("Listing Count", justify="right")
        for operation, count in operation_counts.items():
            table.add_row(operation, str(count))
        ctx.echo(pprint.context_pprint(Padding(table, (1, 0, 0, 0))))
        user_input = input(f"Are you sure you want to push these changes? (yes/no):")
        if user_input.lower() in ['yes', 'y']:
            confirm = True
        print("="*80)
    return confirm

# scan param dictionary for src_file key and open the file specified as the value and return new dictionary with the file handle instead of the path
def find_and_open_src_files(ctx: Any, ops: str, params: Dict) -> Dict:
    for key, value in params.items():
        if key == "src_file":
            if ops in ["draft", "listing-update", "prop-update"]:
                file = open(value, 'r', encoding='utf-8')
            else:
                file = open(value, 'rb')
            params[key] = file
    return params

def push_listing_sync(ctx: Any, root: str, no_preview: bool, silent: bool) -> None:
    ctx.vlog(f"Push Listing Updates from local plan file staged in: {root}")
    listing_ops = get_operations_from_plan(ctx, root)
    cont_flag = False
    if not no_preview:
        cont_flag = push_preview_listing_sync(ctx, listing_ops)
    else:
        cont_flag = True
    if cont_flag:
        ok_cnt = 0
        ctx.vlog(f"Pushing Listing Updates from Plan")
        cmd_cache = {}
        for op in listing_ops:
            cmd = cmd_cache.get(op['operation'], None)
            if not cmd:
                cmd = ctx.root_obj.get_command(ctx, op['operation'])
                cmd_cache[op['operation']] = cmd
            if cmd:
                cc = click.get_current_context()
                if "src_file" in op['params']:
                    op['params'] = find_and_open_src_files(ctx, op['operation'], op['params'])
                    with op['params']['src_file']:
                        res = cc.invoke(cmd, **op['params'])
                else:
                    res = cc.invoke(cmd, **op['params'])
                if res == 0:
                    ok_cnt += 1
                    status = "[green bold]OK[/green bold]"
                else:
                    status = "[red bold]ERROR[/red bold]"
                if not silent:
                    ctx.echo(pprint.context_pprint(f"[yellow bold]FILE:[/yellow bold] {op['src_file']} [red bold]=>[/red bold] [yellow bold]OPS:[/yellow bold] [magenta bold]{op['operation']}[/magenta bold] - [yellow bold]RESULT:[/yellow bold] {status}"))
        tot_cnt = len(listing_ops)
        err_cnt = tot_cnt - ok_cnt
        ctx.vlog(pprint.context_pprint(f"Success: [green]{ok_cnt}[/green] Errored: [red]{err_cnt}[/red] Total: [magenta]{tot_cnt}[/magenta]"))
    return

@click.command("sync-push", short_help="Using the plan file from the sync-plan command to push listing changes.")
@click.option("-R", "--root-folder", required=False, type=click.STRING, default=".", help="Set root folder to locate the staging folder for the operation.")
@click.option("-P", "--no-preview", required=False, default=False, is_flag=True, help="Supress operation preview and confirmatio and push immediately.")
@click.option("-S", "--silent", required=False, default=False, is_flag=True, help="Supress console output.")
@pass_environment
def cli(ctx, root_folder, no_preview, silent) -> int:
    """Perform a PUSH action and run commands from staged plan file in the root."""
    result = 0
    ctx.check_auth("SYNC-PUSH")
    ctx.vlog(f"Process SYNC-PUSH root folder: {root_folder}")
    try:
        push_listing_sync(ctx, root_folder, no_preview, silent)
    except Exception as ex:
        ctx.log(f"Error processing command - {ex}")
        result = 1
    return result
