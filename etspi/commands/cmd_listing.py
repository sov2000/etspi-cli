import click
from etspi.cli import pass_environment

@click.command("listing", short_help="Retrieve listing by ID")
@click.argument("action", type=click.STRING)
@click.option("-i", "--id", required=True, type=click.STRING, help="Listing ID to which apply action.")
@pass_environment
def cli(ctx, action, id):
    """Perform an action on a listing by its ID."""
    ctx.check_auth("LISTING")
    if not id is None:
        ctx.log(f"Retrieve {action} listing {id} - {ctx.home}")
    ctx.log(f"Token: {ctx.token} Refresh: {ctx.refresh_token}")
