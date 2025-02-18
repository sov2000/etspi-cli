# Etsy Shop CLI

Etspi is a command-line tool that empowers Etsy sellers to manage their shops and listings efficiently. The tool is an interface to the [API](https://developers.etsy.com/documentation) 
provided by Etsy and allows viewing and managing the shop and the listings directly with JSON.

## Prerequisites:

- Access to the Etsy API is essential. Review [Etsy Quick Start Guide](https://developers.etsy.com/documentation/tutorials/quickstart) for directions on how to get your personal API key. 
- Familiarize yourself with the Etsy OAuth 2.0 authentication process ([link to Etsy OAuth 2.0 documentation](https://developers.etsy.com/documentation/essentials/authentication))
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
pipx install etspi
```
If you plan to use Etspi to obtain API tokens, you will also need to have `openssl` installed or some other means to generate certificates suitable for SSL/TLS to secure HTTP server. Alternatively, you can use dedicated tools like Postman to obtain tokens manually. However, Etspi offers a more convenient approach, and you only need to do this once if you persist the tokens. Etspi will automatically use persited refresh token to get a fresh API token when necessary.

## Configuration:

Etspi requires `--key`, `--token`, `--refresh-token`, and `--expiry` arguments for all commands excepts the `auth` command which is used to obtain and setup these values. The values for these arguments can be also supplied via environmental variables prefixed by `ETSPI_` followed by argument name, e.g. `ETSPI_TOKEN`, `ETSPI_REFRESH_TOKEN`, etc.

Etspi will also attempt to load these values from `auth.env` file located in `.etspi` folder in user home directory. Etspi will create this folder on first invocation, but the `auth.env` file has to be created by the `auth` command with persist `-tF` flag or manually. The format for the file is standard `.env` file with `key=value` pair on each line. Because the file contains sensitive information, consider securing the file with proper permissions and ensure that it can only be read/written by the user running `etspi`.

The source and the values of the required arguments can be checked by supplying the `-v` flag to `etspi`. This will output `Auth Parameters` table with key, values, and their sources. The possible value sources are COMMANDLINE for command line arguments, ENVIRONMENT for environment variables, and DEFAULT_MAP for `auth.env` file. The precedence is such that environment variable values override the `auth.env` file values and command line arguments override both the variables and the file values.

## Authentication:

Before you can use the app, you will need to obtain an API key from Etsy. You can find more info and how to request a key on the [developer portal](https://www.etsy.com/developers). Etspi assists with authorization and tokens once you've created an app and acquired an API key. If the tokens are saved, they are automatically refreshed as needed upon expiration.

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
    etspi -K YOUR_API_KEY auth -tF
    ```
    - `-tF` flag saves tokens to the `auth.env` file. See `etspi auth --help` for more options.

- The Etspi will compose an Auth URL to start the flow.
- Authenticate with Etsy and authorize your app with the assigned keystring for access to the requested scopes.
- Upon authorization completion, Etsy redirects your browser to the defined callback URL, where Etspi is waiting to obtain the tokens.
- The redirect request contains an authorization code from Etsy that is needed to request the tokens.
- If successful in obtaining the tokens, they are saved in `auth.env` file in the `.etspi/` home folder.
- Most Etspi commands require authorization tokens that can either be pulled from the `auth.env` file, specified as arguments, or set as environment variables in your shell.
    - E.g. `ETSPI_KEY=YOU_ETSY_APP_KEYSTRING` or `ETSPI_TOKEN=YOUR_AUTH_TOKEN`.
    - See *Configuration* section for more details.

## User:

Retrieve current authenticated user ID and Shop ID.

```bash
etspi user
```

More User details can be retrieved for a specific User ID.

```bash
etspi user -u 123456789
```

## Shop:

Retrieve detailed shop info by Shop Id.

```bash
etspi shop-get -s 12345678
```

Same as before but pull info by User ID instead.

```bash
etspi shop-get -u 123456789
```

Alternatively, search by Shop Name performing typical partial name search.

```bash
etspi shop-get -n Paint
```

Since you the number of the results can be quite large, `-R` option can be used to limit and offset the results with the first number as the `offset` and the second number as the `limit` to retrieve.

```bash 
etspi shop-get -n Paint -R 9 1
```

## Shop Find Listings:

### shop-find

Find shop listings by various parameters and metadata. The listings can be filtered by state, section id, or keywords and sorted by Create/Update dates, price, or score. Due to API limitations, you cannot combine state and section id search or state and keyword searches.

Find first 3 listings for the shop.

```bash
etspi shop-find -s 12345678 -R 0 3
```

Same as above, but filter the output with JMESPath expression to only output `listing_id`.

```bash
etspi shop-find -s 12345678 -R 0 3 -q "results[*].listing_id"
```

Find first 5 `draft` listings for the shop.

```bash
etspi shop-find -s 12345678 -R 0 5 -q "results[*].listing_id" -st Draft
```

Find first 5 listings for the shop in `active` state and order by default `Create Date` in ascending order.

```bash
etspi shop-find -s 12345678 -R 0 5 -q "results[*].listing_id" -st Active -so Asc
```

Same as above, but this time find the listings by `Updated Date`.

```bash
etspi shop-find -s 12345678 -R 0 5 -q "results[*].listing_id" -st Active -so Asc -ss Updated
```

Find first 5 `active` listings for the shop ordered by `Price` and display `listing_id` and `title` for each.

```bash
etspi shop-find -s 12345678 -R 0 5 -q "results[*].{listing_id: listing_id, title: title}" -st Active -so Asc -ss Price
```

Find first 5 listings by `Section ID` with `-si` flag and order the result in descending order by `Created Date`.

```bash
etspi shop-find -s 12345678 -si 12345678 -R 0 5 -q "results[*].{listing_id: listing_id, title: title}" -so Desc -ss Created
```

Find first 5 listings by keyword using `-K` flag and order the result in descending order by `Created Date`'

```bash
etspi shop-find -s 12345678 -K "lily" -R 0 5 -q "results[*].{listing_id: listing_id, title: title}" -so Desc -ss Created
```

## Listing:

The following commands are used to create, update, and delete the listings along with basic listing information like title, description, tags, shipping profile, etc.

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

This is self-explanatory and will delete a listing by Id. Use `-Y` or `--yes` flag to suppress ***confirmation prompt*** before making the API call to delete the listing!

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

## Images:

### image-get

Display all listing Images with IDs, URLs, and other metadata.

```bash
etspi image-get -i 1800000081
```

Or if information is only needed for one image, pull it by Image ID in addition to the listing ID.

```bash
etspi image-get -i 1800000081 -ii 6123123123
```
### image-upload

Upload a new image and add it to the listing at the specified `rank` with option `-r` and `-a` for alternate text. If you are uploading into existing `rank`, you will need `-O` option to allow overwriting of the content.

```bash
etspi image-upload -i 1800000081 -s 12345678 -f "path\to\my\Listing_Image_File.jpg" -r 5 -a "Tree print wall art"
```

### image-delete

Delete an image from listing by Image Id. Use `-Y` or `--yes` flag to suppress ***confirmation prompt*** before making the API call to delete.

```bash
etspi image-delete -i 1800000081 -ii 6123123123
```

## Videos:

### video-get

Display all listing Videos with IDs, URLs, and other metadata. Use this method if you do not have Video ID.

```bash
etspi video-get -i 1800000081
```

Or if information is only needed for one video and you have the ID, pull it by Video ID in addition to the listing ID.

```bash
etspi video-get -i 1800000081 -vi 6123123123
```

### video-upload

Upload a new video or update an existing video by Listing ID and Video ID.

```bash
etspi video-upload -i 1800000081 -s 12345678 -f "path\to\my\Listing_Video_File.mp4"
```

Or to update an existing video by Video ID. Supplying Video ID is redundant because, at the moment, Etsy only supports one listing video.

```bash
etspi video-upload -i 1800000081 -s 12345678 -f "path\to\my\Listing_Video_File.mp4" -vi 6123123123
```

### video-delete

Delete a video from listing by Video ID. Use `-Y` or `--yes` flag to suppress ***confirmation prompt*** before making the API call to delete.

```bash
etspi video-delete -i 1800000081 -s 12345678 -vi 6123123123 -Y
```

## Files:

File commands are used to manage file assets for digital listings. Etsy will convert a physical listing to digital if you associate a file with an existing physical listing. Similarly, a digital listing will convert to a physical one when you delete the last file from the listing.

### file-get

Display all listing Files with ID, name, size, type, etc. Use this method if you do not have a specific File ID.

```bash
etspi file-get -i 1800000081 -s 12345678
```

Or if information is only needed for one file and you have the ID, pull it by File ID in addition to the listing ID.

```bash
etspi file-get -i 1800000081 -s 12345678 -fi 13123123123123
```

### file-upload

Upload a new file from a local path.

```bash
etspi file-upload -i 1800000081 -s 12345678 -f "path\to\my\Listing_Digital_Content_File.pdf"
```

Use the `-r` or `--rank` argument to manipulate the file at the `rank` position in the list of multiple files.

```bash
etspi file-upload -i 1800000081 -s 12345678 -f "path\to\my\Listing_Digital_Content_File.pdf" -r 2
```

Or to associate an existing file with File ID to Listing ID. 

```bash
etspi file-upload -i 1800000081 -s 12345678 -fi 13123123123123
```

### file-delete

Delete a file from listing by File ID. Use `-Y` or `--yes` flag to suppress ***confirmation prompt*** before making the API call to delete.

```bash
etspi file-delete -i 1800000081 -s 12345678 -fi 13123123123123 -Y
```

## Properties:

### prop-get:

To retrieve all properties for a listing.

```bash
etspi prop-get -i 1800000081 -s 12345678
```

To retrieve a specific property (with ID 98765432) for a listing

```bash
etspi prop-get -i 1800000081 -s 12345678 -pi 98765432
```

To retrieve all properties for a listing and save the output to a file named "listing_properties.json"

```bash
etspi prop-get -i 1800000081 -s 12345678 -o listing_properties.json
```

To retrieve all properties for a listing, format the output for a listing property update request, and save the output to a file named "listing_property_update.json"

```bash
etspi prop-get -i 1800000081 -s 12345678 --format-update -o listing_property_update.json
```

### prop-update

To update a property for listing, you will need a JSON file in the correct update format. Use the `prop-get` command to generte a file you can modify in the correct format.


```bash
etspi prop-update -i 1800000081 -s 12345678 -pi 98765432 -f listing_property_update.json
```

## Note on STDOUT redirects

Etspi console output uses `rich` library `print` which will color code and format JSON for more esthetic and readable output. When using Etspi `--out` you get original formatted JSON which is what you want for subsequent commands and API calls. If you have a need to pipe or redirect Etspi output to a different console app or file, you may want this original JSON and not pretty formatted. In that case, consider using `--out` to STDOUT `-` with `-S` and apply your pipe or redirect this way.

```bash
etspi listing-get -i 1800000081 -in Inventory -S -o - | grep "sku"
```
