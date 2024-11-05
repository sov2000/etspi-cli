import datetime
import os
import ssl
import click
import threading
import time
import http.server
import urllib.parse
import json

import rich.box
from typing import Any, Dict, List, Optional
from rich import print
from rich.console import Console
from rich.panel import Panel
from etspi.cli import pass_environment, Environment
from etsyv3.util.auth import AuthHelper

HTTPD_ACTIVE = True

# generate certs with openssl
# openssl req -nodes -x509 -newkey rsa:2048 -keyout %USERPROFILE%\.etspi\key.pem -out %USERPROFILE%\.etspi\cert.pem -days 365

# http request handler to receive auth code from etsy and get an auth token
class EtspiAuthRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global HTTPD_ACTIVE
        ctx = self.server.command_context
        if "etspi" in self.path:
            ctx.vlog(f"Starting callback request handler - {self.path}")
            query_components = urllib.parse.urlparse(self.path).query
            query_params = urllib.parse.parse_qs(query_components)

            status_code = 0
            msg = "<h1>Authorization - <span style='color: %s'>%s</span></h1><h3>Postback completed %s.</h3><div>%s</div><div>%s</div>"
            if "code" in query_params:
                state = query_params.get('state', [''])[0]
                code = query_params.get('code', [''])[0]
                ctx.vlog(f"Found authorization code: {code}")

                if not code == '' and state == ctx.auth_helper.state:
                    ctx.vlog(f"Authorization state is present and valid: {state}")
                    status_code = 200
                    resp = ("green", "Success", "successfully", "<b>State:</b> {}".format(state),
                            "<b>Code:</b> {}".format(code))
                    
                    ctx.auth_helper.set_authorisation_code(code, state)
                    ctx.vlog("Requesting authorization tokens")
                    d_token = ctx.auth_helper.get_access_token()
                    
                    ctx.log("Successfully obtained access tokens")
                    ctx.token = d_token['access_token']
                    ctx.refresh_token = d_token['refresh_token']
                    ctx.expiry = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=d_token["expires_in"])

                    if not ctx.options["token-hidden"]:
                        ctx.log(f"access_token: {d_token['access_token']}")
                        ctx.log(f"refresh_token: {d_token['refresh_token']}")
                        ctx.log("expiry: {}".format(ctx.expiry.strftime("%Y-%m-%d %H:%M:%S")))

                    if ctx.options["token-file"]:
                        Environment.save_auth_config(ctx.get_auth_params_asdic())
                        ctx.log("Updated auth.env file with token data")
                else:
                    ctx.vlog(f"Authorization state is not valid: {state}")
                    status_code = 403
                    error = "unauthorized_client"
                    error_desc = "Invalid authorization code or state"
                    resp = ("red", "Error", "with errors", "<b>Error:</b> {}".format(error),
                            "<b>Description:</b> {}".format(error_desc))
            else:
                ctx.vlog(f"Authorization callback returned with errors")
                status_code = 403
                error = query_params.get('error', [''])[0]
                error_desc = query_params.get('error_description', [''])[0]
                resp = ("red", "Error", "with errors", "<b>Error:</b> {}".format(error), 
                        "<b>Description:</b> {}".format(error_desc))

            self.send_response(status_code)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            msg %= resp
            self.wfile.write(msg.encode())

            ctx.log("Handling callback request finished")
            HTTPD_ACTIVE = False
        else:
            ctx.vlog(f"Skipping handling callback request - {self.path}")

# subclass http server to inject our command context for the handler
class EtspiHTTPServer(http.server.HTTPServer):
    def __init__(self, server_address: tuple, RequestHandlerClass, bind_and_activate: bool = True, command_context: Any = None):
        self.command_context = command_context
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)

def get_redirect_url(ctx: Any, host: str, port: int) -> str:
    rdr_u = "https://{}:{}/etspi".format(host, port)
    ctx.vlog(f"Redirect URL used for auth: {rdr_u}")
    return rdr_u

def start_httpd_service(ctx: Any, host: str, port: int, certfile: str, keyfile: str) -> EtspiHTTPServer:
    httpd = EtspiHTTPServer((host, port), EtspiAuthRequestHandler, bind_and_activate = True, command_context = ctx)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)
    srv_thrd = threading.Thread(target=httpd.serve_forever, daemon=True)
    srv_thrd.start()
    return httpd

def check_all_scopes(scopes: List) -> List:
    if "all" in scopes:
        return ["feedback_r", "listings_d", "listings_r", "listings_w", "shops_r", "shops_w", "transactions_r", "transactions_w"]
    return scopes

def get_auth_directions(ctx: Any, auth_hlp: AuthHelper, rdr_url: str, scope_list: list) -> None:
    auth_url, state = auth_hlp.get_auth_code()
    ctx.vlog(f"Auth State: {state}")
    ctx.vlog(f"Auth Code Verifier: {auth_hlp.code_verifier}")
    ctx.vlog(f"Auth Code Challange: {auth_hlp.code_challenge}")
    ctx.vlog("Auth Scopes: {}".format(" ".join(scope_list) if not scope_list is None else "Undefined"))
    ctx.log(f"Click or copy/paste this link and authenticate to start authorization flow...")
    ctx.echo("-" * 60)
    ctx.echo(auth_url)
    ctx.echo("-" * 60)

@click.command("auth", short_help="Setup API authorization")
@click.option("-h", "--host", required=True, default="localhost", type=click.STRING, help="Callback server host name or ip.")
@click.option("-p", "--port", required=True, default=10443, type=click.INT, help="Callback server port number.")
@click.option("-c", "--certfile", required=True, 
              type=click.Path(exists=True, file_okay=True, resolve_path=True),
              default=os.path.join(os.path.expanduser('~'), ".etspi\\cert.pem"),
              help="Callback server SSL certificate file location.")
@click.option("-k", "--keyfile", required=True, 
              type=click.Path(exists=True, file_okay=True, resolve_path=True), 
              default=os.path.join(os.path.expanduser('~'), ".etspi\\key.pem"), 
              help="Callback server SSL key file location.")
@click.option("-s", "--scope", multiple=True, default=["all"],
              type=click.Choice(["all", "feedback_r", "listings_d", "listings_r", "listings_w", "shops_r", "shops_w", "transactions_r", "transactions_w"], case_sensitive=True), 
              help="Specify scope options to request for authorization or 'all' for all currently supported scopes.")
@click.option("-tF", "--token-file", is_flag=True, default=False, help="Write out the tokens to the auth.env file.")
@click.option("-tH", "--token-hidden", is_flag=True, default=False, help="Supress the output of the tokens to the console.")
@pass_environment
def cli(ctx: Any, host: Any, port: Any, certfile: Any, keyfile: Any, scope: Any, token_file: bool, token_hidden: bool) -> None:
    """Host local redirect endpoint and help guide through the authorization flow to obtain Etsy API token that is used with the API."""
    ctx.vlog(f"Loaded command module - AUTH")
    ctx.options["token-file"] = token_file
    ctx.options["token-hidden"] = token_hidden
    rdr_url = get_redirect_url(ctx, host, port)
    ctx.auth_helper = AuthHelper(ctx.keystring, rdr_url, scopes=check_all_scopes(scopes=scope))
    get_auth_directions(ctx, ctx.auth_helper, rdr_url, scope)
    httpd = start_httpd_service(ctx, host, port, certfile, keyfile)
    ctx.log("Expecting authorization redirect request... Ctr+C to force Abort")
    ctx.log(f"Redirect request - URL: {rdr_url}")
    for i in range(3000):
        if i % 100 == 0:
            trem = int((3000-i)/5)
            ctx.log(f"Waiting for redirect ... abort in {trem} sec.")
        if not HTTPD_ACTIVE:
            break
        time.sleep(0.2)
    httpd.shutdown()
