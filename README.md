# Etsy Shop CLI

Etspi is a command line tool to help Etsy sellers manage their shop and listings. The tool is an interface to the [API](https://developers.etsy.com/documentation) 
provided by Etsy and allows viewing and managing the shop and the listings in more direct way with JSON data. Access to the API is a prerequisite, but
the tool does provide some commands and features to help obtaining and managing access tokens. See the following Auth section for details. All of the 
output command support [JMESPath expressions](https://jmespath.org/examples.html) to filter and transform the data.

## Features
- Authentication and authorization helper command
- Automatic token rotation and management
- Manage listings and inventory
- Transform and filter output with JMESPath 

## Installation

## Authentication

Before you can use the app, you will need to obtain an API key from Etsy. You can find more info and how to request a key on the [developer portal](https://www.etsy.com/developers). There is also detailed information about the OAuth 2.0 [authentication flow](https://developers.etsy.com/documentation/essentials/authentication) there. The Etspi tool can help with the authorization and tokens once you create an app and obtain an API key. 

- Note the Keystring from the App settings. You will need it to start the auth flow.
- In the App settings, you will also need to add a callback URL for the Etspi that will be used in the auth flow.
    - By default, it's https://localhost:10443/etspi, but it can change depending on the settings you use for the host and port flags, if you chose to override the dafaults.
- Before you start the auth flow with Etspi, you will also need to create a self-signed SSL certificate/key pair for the CLI to use.
    - This step is necessary as it is an Etsy requirement that the redirect callback URLs are SSL protected and contain HTTPS prefix.
    - You will need OpenSSL installation for this step.
    - Run the following from the command prompt/terminal to get the cert/key pair and save them to your home Etspi directory.
    - Linux/MacOS: `openssl req -nodes -x509 -newkey rsa:2048 -keyout ~/.etspi/key.pem -out ~/.etspi/cert.pem -days 365`
    - Windows: `openssl req -nodes -x509 -newkey rsa:2048 -keyout %USERPROFILE%\.etspi\key.pem -out %USERPROFILE%\.etspi\cert.pem -days 365`
- To start the auth flow for all scopes, default redirect URL, and cert/key files from prior step:
- `python etspi-run.py auth -tF`
- The Etspi will compose an Auth URL to start the flow.
- You will need to authenticate with Etsy and authorize your App with assigned Keystring for the scopes requested.
- Once complete, Etsy will redirect your browser to the default redirect URL that the Etspi is waiting on to request the tokens.
- The redirect request contains and authorization code from Etsy that is needed to request the tokens.
- If successful in obtaining the tokens, they are saved in `Auth.env` file in the `.etspi/` home folder.
- Most Etspi commands require authorization tokens that can either be pulled from the `Auth.env` file, specified on the command line, or set as environment variables in your shell.
    - E.g. `ETSPI_KEY=YOU_ETSY_APP_KEYSTRING` or `ETSPI_TOKEN=YOUR_AUTH_TOKEN`.
    - Command line options take precedence over the env variables and variables take precedence over the values stored in the `Auth.env` file.