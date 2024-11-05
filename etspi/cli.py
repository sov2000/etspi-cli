import os
import sys
import datetime

from etsyv3 import EtsyAPI
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv, dotenv_values

import click

__version__ = "1.0.1"

# Click context and environment utility class
class Environment:
    def __init__(self):
        self.verbose = False
        self.home = os.getcwd()
        self.etsy = None
        self.auth_helper = None
        self.options = {}

    def set_auth_params(self, token: str, refresh_token: str, key: str, expiry: str) -> None:
        self.keystring = key
        self.token = token
        self.refresh_token = refresh_token
        epoch_time = datetime.datetime.fromtimestamp(int(expiry))
        self.expiry = epoch_time

    def get_auth_params_asdic(self) -> Dict[str, str]:
        epoch_time = str(int(self.expiry.timestamp()))
        return {"token": self.token, "refresh_token": self.refresh_token, "key": self.keystring, "expiry": epoch_time}

    def check_auth(self, argument: str) -> None:
        if not self.keystring or not self.token or not self.refresh_token or not self.expiry:
            raise click.BadArgumentUsage(f"{argument} argument is missing required authentication parameters")
        
    def get_etsy(self, argument: str) -> EtsyAPI:
        self.check_auth(argument=argument)
        if self.etsy is None:
            persist_clbck = self.save_tokens_refresh if not "no-persist" in self.options else None
            self.etsy = EtsyAPI(self.keystring, self.token, self.refresh_token, self.expiry, persist_clbck)
        return self.etsy

    def save_tokens_refresh(self, access_token: str, refresh_token: str, expires_at: datetime) -> None:
        self.vlog("Updating auth.env file with refreshed token data")
        self.token = access_token
        self.refresh_token = refresh_token
        self.expiry = expires_at
        Environment.save_auth_config(self.get_auth_params_asdic())
        self.vlog(f"access_token: {access_token}")
        self.vlog(f"refresh_token: {refresh_token}")
        self.vlog("expiry: {}".format(expires_at.strftime("%Y-%m-%d %H:%M:%S")))
        return

    def log(self, msg: str, *args: list) -> None:
        if args:
            msg %= args
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        click.echo(f"[{ts}] {msg}", file=sys.stderr)

    def vlog(self, msg: str, *args: list) -> None:
        if self.verbose:
            self.log(msg, *args)
    
    def echo(self, msg: str, *args: list) -> None:
        if args:
            msg %= args
        click.echo(msg, file=sys.stderr)

    @staticmethod
    def load_auth_config() -> Dict[str, str]:
        user_home = os.path.expanduser('~')
        dotenv_path = os.path.join(user_home, ".etspi\\auth.env")
        if os.path.isfile(dotenv_path):
            return dotenv_values(dotenv_path)
        return
    
    @staticmethod
    def save_auth_config(auth_vars: Dict[str, str]):
        user_home = os.path.expanduser('~')
        dotenv_path = os.path.join(user_home, ".etspi\\auth.env")
        with open(dotenv_path, 'w') as f:
            for key, value in auth_vars.items():
                f.write(f"{key}={value}\n")

# Click CLI root command class and main entry point
class EtspiCLI(click.Group):
    def list_commands(self, ctx: click.Context) -> List:
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py") and filename.startswith("cmd_"):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx: click.Context, name: str) -> Any:
        try:
            mod = __import__(f"etspi.commands.cmd_{name}", None, None, ["cli"])
        except ImportError as ex:
            click.echo(f"Failed to load commnad module - {ex.msg}", file=sys.stderr)
            return
        return mod.cli

def show_auth_params(root: click.Context, ctx: Any) -> None:
    console = Console()
    table = Table(title="Auth Parameters")
    table.add_column("Parameter", justify="left", header_style="green")
    table.add_column("Value", justify="left", header_style="green")
    table.add_column("Source", justify="left", header_style="green")
    for ap in ["key", "token", "refresh_token", "expiry"]:
        value, source = (root.params[ap], root.get_parameter_source(ap).name) if ap in root.params else ("NOT FOUND", "MISSING")
        table.add_row(ap, value, source)
    with console.capture() as capture:
        console.print(table)
    ctx.echo(capture.get())

CONTEXT_SETTINGS = dict(auto_envvar_prefix="ETSPI", default_map=Environment.load_auth_config())
pass_environment = click.make_pass_decorator(Environment, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "commands"))

@click.command(cls=EtspiCLI, context_settings=CONTEXT_SETTINGS)
@click.option("--home", type=click.Path(exists=True, file_okay=False, resolve_path=True), help="Set a directory for input and output commnads.")
@click.option("-T", "--token", required=False, help="API access token obtained with the AUTH command.")
@click.option("-RT", "--refresh-token", required=False, help="API refresh token obtained with the AUTH command.")
@click.option("-K", "--key", required=False, help="API access key issued by Etsy.")
@click.option("-E", "--expiry", required=False, help="API access token future expiration timestamp.")
@click.option("-nP", "--no-persist", is_flag=True, default=False, help="Do not update auth.env file when tokens are refreshed. By default, if the file exists, new tokens are automatically saved.")
@click.option("-v", "--verbose", is_flag=True, help="Enables verbose output mode.")
@pass_environment
@click.pass_context
def cli(root: Any, ctx: Any, home: Any, token: Any, refresh_token: Any, key: Any, expiry: Any, no_persist: bool, verbose: Any) -> None:
    """Command line app to interact with Etsy V3 API for shop management."""
    ctx.verbose = verbose
    ctx.set_auth_params(token, refresh_token, key, expiry)
    if home is not None:
        ctx.home = home
    if no_persist:
        ctx.options["no-persist"] = True
    if ctx.verbose:
        show_auth_params(root, ctx)