# Etsy Shop CLI

Etspi is a command-line tool that empowers Etsy sellers to manage their shops and listings efficiently. The tool is an interface to the [API](https://developers.etsy.com/documentation) 
provided by Etsy and allows viewing and managing the shop and the listings directly with JSON.

## Prerequisites:

- Access to the Etsy API is essential. Review [Etsy Quick Start Guide](https://developers.etsy.com/documentation/tutorials/quickstart) for directions on how to get your personal API key. 
- Etspi doesn't provide API key assistance, but it can help with authorization and managing access tokens (explained in the **Authentication** section).
- Familiarity with JMESPath expressions ([link to JMESPath examples](https://jmespath.org/examples.html)) is recommended to filter and transform output data.

## Features:
- **Easy Authentication and Authorization:** Etspi guides you through the process of obtaining and managing API tokens.
- **Automatic Token Management:** Etspi simplifies token maintenance by automatically refreshing access tokens as needed (if configured).
- **Listing Management:** Handle shop listings and variant inventory directly from the command line.
- **Flexible Output Filtering:** Tailor output using JMESPath expressions to retrieve only the data you need.
- **Streamlined Request Formatting:** Transform listing data effortlessly into the appropriate format for draft, listing, or inventory operations.

## Installation:

The recommended installation method is via `pipx`. Refer to the official `pipx` documentation ([link to pipx doc site](https://pipx.pypa.io/stable/)) for installation and usage instructions.

```bash
pipx install etspi-1.0.1
```
If you plan to use Etspi to obtain API tokens, you will also need to have `openssl` installed or some other means to generate certificates suitable for SSL/TLS to secure HTTP server. Alternatively, you can use dedicated tools like Postman to obtain tokens manually. However, Etspi offers a more convenient approach, and you only need to do this once if you persist the tokens. Etspi will automatically use persited refresh token to get a fresh API token when necessary.

## Authentication:

Before you can use the app, you will need to obtain an API key from Etsy. You can find more info and how to request a key on the [developer portal](https://www.etsy.com/developers). Familiarize yourself with the Etsy OAuth 2.0 authentication process ([link to Etsy OAuth 2.0 documentation](https://developers.etsy.com/documentation/essentials/authentication)). Etspi assists with authorization and tokens once you've created an app and acquired an API key.

- Note the Keystring from the App settings. You will need it to start the auth flow.
- In the App settings, you will also need to add a callback URL for the Etspi that will be used in the auth flow.
    - By default, it's https://localhost:10443/etspi, but it can be customized using Etspi flags.
- Before you start the auth flow with Etspi, you will also need to create a self-signed SSL certificate/key pair for the tool to use.
    - This step is necessary as it is an Etsy requirement that the redirect callback URLs are SSL protected and contain HTTPS prefix.
    - You will need OpenSSL installation for this step.
    - Run the following from the command prompt/terminal to get the cert/key pair and save them to your home Etspi directory.
    - Linux/MacOS:

    ```bash
    openssl req -nodes -x509 -newkey rsa:2048 -keyout ~/.etspi/key.pem -out ~/.etspi/cert.pem -days 365
    ```
    - Windows:
    
    ```cmd
    openssl req -nodes -x509 -newkey rsa:2048 -keyout %USERPROFILE%\.etspi\key.pem -out %USERPROFILE%\.etspi\cert.pem -days 365
    ```

- To start the auth flow for all scopes, default redirect URL, and cert/key files from the prior step:
    ```bash
    etspi auth -tF
    ```
    - `-tF` flag saves tokens to the `Auth.env` file. See `etspi auth --help` for more options.

- The Etspi will compose an Auth URL to start the flow.
- Authenticate with Etsy and authorize your app with the assigned keystring for access to the requested scopes.
- Upon authorization completion, Etsy redirects your browser to the defined callback URL, where Etspi is waiting to obtain the tokens.
- The redirect request contains an authorization code from Etsy that is needed to request the tokens.
- If successful in obtaining the tokens, they are saved in `Auth.env` file in the `.etspi/` home folder.
- Most Etspi commands require authorization tokens that can either be pulled from the `Auth.env` file, specified on the command line, or set as environment variables in your shell.
    - E.g. `ETSPI_KEY=YOU_ETSY_APP_KEYSTRING` or `ETSPI_TOKEN=YOUR_AUTH_TOKEN`.
    - Command line options take precedence over the env variables and variables take precedence over the values stored in the `Auth.env` file.

## Listing:

### listing-get

The most basic use case is to pull listing data by its Id.

```bash
etspi listing-get -i 1800000081
```
Include `-in` flag and option `value` to also include additional data; combine several `values` as needed.

```bash
etspi listing-get -i 1800000081 -in Images -in Shipping
```

Include `-q` or `--query` flag and JMESPath expression to filter and shape the output JSON. 

```bash
etspi listing-get -i 1800000081 -q "{ id: listing_id, title: title }"
```

Etsy listing JSON structure from `listing-get` command and `draft` or `listing-update` commands are not symmetrical. If you'd like to create a new draft from existing or update a listing, you will likely want to transform the JSON output into the format ready for `draft` or `listing-update` commands. Use `--format-draft` or `--format-update` flags and combine with `-o` flag to save the result into a file you can modify and later use with each command.

```bash
etspi listing-get -i 1800000081 -in Images --format-draft -o my_listing.json
```
### draft

Create a new draft listing from a JSON data source file. To publish your draft you will need to use the `listing-update` command and set the `state` field to `active`. *Expect Etsy to charge the **listing fee** when you activate the draft.*

```bash
etspi draft -s 10000001 -f my_draft_listing.json
```

### listing-update

Like the `draft` command, you update the listing with the values from a JSON source file specified on the command line.

```bash
etspi listing-update -i 1800000081 -s 10000001 -f my_listing_update.json
```

### listing-delete

This is self-explanatory and will delete a listing by Id. Use `-Y` or `--yes` flat to suppress ***confirmation prompt*** before making the API call to delete the listing!

```bash
etspi listing-delete -i 1800000081 -Y
```

### listing-get-iv

Retrieves the inventory record for a listing by Id.

```bash
etspi listing-get-iv -i 1800000081
```

Include `-q` or `--query` flag and JMESPath expression to filter and shape the output JSON. 

```bash
etspi listing-get-iv -i 1800000081 -q "products[?offerings[0].price.amount > `1000`].[product_id, sku]"
```

Use `--format-update` and `-o` flags to transform the output into format suitable for `listing-update-iv` command.

```bash
etspi listing-get-iv -i 1800000081 --format-update -o my_listing_inventory.json
```

### listing-update-iv

Use to update the listing inventory with the values from a JSON source file specified on the command line.

```bash
etspi listing-update-iv -i 1800000081 -f my_listing_update.json
```

## Note on STDOUT redirects

Etspi console output uses `rich` library `print` which will color code and format JSON for more esthetic and readable output. When using Etspi `--out` you get original formatted JSON which is what you want for subsequent commands and API calls. If you have a need to pipe or redirect Etspi output to a different console app or file, you may want this original JSON and not pretty formatted. In that case, consider using `--out` to STDOUT `-` with `-S` and apply your pipe or redirect this way.

```bash
etspi listing-get -i 1800000081 -in Inventory -S -o - | grep "sku"
```
