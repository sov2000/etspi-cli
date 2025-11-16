"""
Pydantic schemas for ETSPI MCP tool parameters

Defines the input parameters for each MCP tool with validation and documentation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Authentication Tools
# ============================================================================

class GetUserInfoParams(BaseModel):
    """Parameters for etspi_get_user_info tool"""
    user_id: Optional[int] = Field(
        default=None,
        description="Specific user ID to retrieve. If not provided, returns authenticated user info."
    )
    query: Optional[str] = Field(
        default=None,
        description="JMESPath query to filter/transform the response"
    )


# ============================================================================
# Shop Tools
# ============================================================================

class GetShopParams(BaseModel):
    """Parameters for etspi_get_shop tool"""
    shop_id: Optional[int] = Field(
        default=None,
        description="Shop ID to retrieve"
    )
    user_id: Optional[int] = Field(
        default=None,
        description="User ID to find shops for"
    )
    shop_name: Optional[str] = Field(
        default=None,
        description="Shop name to search for (partial match)"
    )
    limit: Optional[int] = Field(
        default=25,
        description="Maximum number of results (when searching)"
    )
    offset: Optional[int] = Field(
        default=0,
        description="Number of results to skip (pagination)"
    )
    query: Optional[str] = Field(
        default=None,
        description="JMESPath query to filter/transform the response"
    )


class FindShopListingsParams(BaseModel):
    """Parameters for etspi_find_shop_listings tool"""
    shop_id: int = Field(
        description="The Etsy shop ID to search listings in"
    )
    section_id: Optional[int] = Field(
        default=None,
        description="Filter by shop section ID"
    )
    state: Optional[str] = Field(
        default=None,
        description="Filter by listing state: Active, Inactive, Draft, SoldOut, or Expired"
    )
    keywords: Optional[str] = Field(
        default=None,
        description="Search keywords to filter listings"
    )
    sort_on: Optional[str] = Field(
        default=None,
        description="Sort field: Created, Updated, Price, or Score"
    )
    sort_order: Optional[str] = Field(
        default=None,
        description="Sort order: Asc or Desc"
    )
    include: Optional[List[str]] = Field(
        default=None,
        description="Additional data to include: Shipping, Images, Shop, User, Translations, Inventory, Videos"
    )
    limit: Optional[int] = Field(
        default=25,
        description="Maximum number of results"
    )
    offset: Optional[int] = Field(
        default=0,
        description="Number of results to skip (pagination)"
    )
    query: Optional[str] = Field(
        default=None,
        description="JMESPath query to filter/transform the response"
    )


# ============================================================================
# Listing Management Tools
# ============================================================================

class GetListingParams(BaseModel):
    """Parameters for etspi_get_listing tool"""
    listing_id: int = Field(
        description="The Etsy listing ID to retrieve"
    )
    include: Optional[List[str]] = Field(
        default=None,
        description="Additional data to include: Shipping, Images, Shop, User, Translations, Inventory, Videos"
    )
    format_as_draft: Optional[bool] = Field(
        default=False,
        description="Transform response to draft listing format suitable for creating new listings"
    )
    format_as_update: Optional[bool] = Field(
        default=False,
        description="Transform response to update listing format suitable for updating listings"
    )
    query: Optional[str] = Field(
        default=None,
        description="JMESPath query to filter/transform the response"
    )


class CreateDraftListingParams(BaseModel):
    """Parameters for etspi_create_draft_listing tool"""
    shop_id: int = Field(
        description="The Etsy shop ID to create the listing in"
    )
    listing_data: Dict[str, Any] = Field(
        description=(
            "JSON object containing listing details. Required fields: "
            "quantity, title, description, price, who_made, when_made, taxonomy_id. "
            "See Etsy API documentation for complete field list."
        )
    )


class UpdateListingParams(BaseModel):
    """Parameters for etspi_update_listing tool"""
    shop_id: int = Field(
        description="The Etsy shop ID containing the listing"
    )
    listing_id: int = Field(
        description="The listing ID to update"
    )
    listing_data: Dict[str, Any] = Field(
        description="JSON object containing fields to update"
    )


class DeleteListingParams(BaseModel):
    """Parameters for etspi_delete_listing tool"""
    listing_id: int = Field(
        description="The listing ID to delete"
    )
    confirm: Optional[bool] = Field(
        default=False,
        description="Set to true to skip confirmation prompt"
    )


# ============================================================================
# Inventory Management Tools
# ============================================================================

class GetListingInventoryParams(BaseModel):
    """Parameters for etspi_get_listing_inventory tool"""
    listing_id: int = Field(
        description="The listing ID to get inventory for"
    )
    format_as_update: Optional[bool] = Field(
        default=False,
        description="Transform response to update inventory format"
    )
    query: Optional[str] = Field(
        default=None,
        description="JMESPath query to filter/transform the response"
    )


class UpdateListingInventoryParams(BaseModel):
    """Parameters for etspi_update_listing_inventory tool"""
    listing_id: int = Field(
        description="The listing ID to update inventory for"
    )
    inventory_data: Dict[str, Any] = Field(
        description="JSON object containing inventory details including products, price_on_property, quantity_on_property, and sku_on_property"
    )


# ============================================================================
# Image Management Tools
# ============================================================================

class GetListingImagesParams(BaseModel):
    """Parameters for etspi_get_listing_images tool"""
    listing_id: int = Field(
        description="The listing ID to get images for"
    )
    image_id: Optional[int] = Field(
        default=None,
        description="Specific image ID to retrieve (optional)"
    )
    query: Optional[str] = Field(
        default=None,
        description="JMESPath query to filter/transform the response"
    )


class UploadListingImageParams(BaseModel):
    """Parameters for etspi_upload_listing_image tool"""
    shop_id: int = Field(
        description="The Etsy shop ID"
    )
    listing_id: int = Field(
        description="The listing ID to upload image to"
    )
    image_data: Optional[str] = Field(
        default=None,
        description="Base64-encoded image data (use this OR image_uri)"
    )
    image_uri: Optional[str] = Field(
        default=None,
        description="URI to image file: file:// for local files, http(s):// for URLs (use this OR image_data)"
    )
    image_id: Optional[int] = Field(
        default=None,
        description="Existing image ID to update (optional, for updates only)"
    )
    rank: Optional[int] = Field(
        default=None,
        description="Position of image in listing (1-based index)"
    )
    alt_text: Optional[str] = Field(
        default=None,
        description="Alternative text for accessibility"
    )
    overwrite: Optional[bool] = Field(
        default=False,
        description="Whether to overwrite existing image"
    )
    watermark: Optional[bool] = Field(
        default=False,
        description="Whether to apply watermark"
    )


class DeleteListingImageParams(BaseModel):
    """Parameters for etspi_delete_listing_image tool"""
    listing_id: int = Field(
        description="The listing ID"
    )
    image_id: int = Field(
        description="The image ID to delete"
    )
    confirm: Optional[bool] = Field(
        default=False,
        description="Set to true to skip confirmation prompt"
    )


# ============================================================================
# Video Management Tools
# ============================================================================

class GetListingVideosParams(BaseModel):
    """Parameters for etspi_get_listing_videos tool"""
    listing_id: int = Field(
        description="The listing ID to get videos for"
    )
    video_id: Optional[int] = Field(
        default=None,
        description="Specific video ID to retrieve (optional)"
    )
    query: Optional[str] = Field(
        default=None,
        description="JMESPath query to filter/transform the response"
    )


class UploadListingVideoParams(BaseModel):
    """Parameters for etspi_upload_listing_video tool"""
    shop_id: int = Field(
        description="The Etsy shop ID"
    )
    listing_id: int = Field(
        description="The listing ID to upload video to"
    )
    video_data: Optional[str] = Field(
        default=None,
        description="Base64-encoded video data (use this OR video_uri)"
    )
    video_uri: Optional[str] = Field(
        default=None,
        description="URI to video file: file:// for local files, http(s):// for URLs (use this OR video_data)"
    )
    video_id: Optional[int] = Field(
        default=None,
        description="Existing video ID to update (optional, for updates only)"
    )


class DeleteListingVideoParams(BaseModel):
    """Parameters for etspi_delete_listing_video tool"""
    shop_id: int = Field(
        description="The Etsy shop ID"
    )
    listing_id: int = Field(
        description="The listing ID"
    )
    video_id: int = Field(
        description="The video ID to delete"
    )
    confirm: Optional[bool] = Field(
        default=False,
        description="Set to true to skip confirmation prompt"
    )


# ============================================================================
# File Management Tools (Digital Products)
# ============================================================================

class GetListingFilesParams(BaseModel):
    """Parameters for etspi_get_listing_files tool"""
    shop_id: int = Field(
        description="The Etsy shop ID"
    )
    listing_id: int = Field(
        description="The listing ID to get files for"
    )
    file_id: Optional[int] = Field(
        default=None,
        description="Specific file ID to retrieve (optional)"
    )
    query: Optional[str] = Field(
        default=None,
        description="JMESPath query to filter/transform the response"
    )


class UploadListingFileParams(BaseModel):
    """Parameters for etspi_upload_listing_file tool"""
    shop_id: int = Field(
        description="The Etsy shop ID"
    )
    listing_id: int = Field(
        description="The listing ID to upload file to"
    )
    file_data: Optional[str] = Field(
        default=None,
        description="Base64-encoded file data (use this OR file_uri, or file_id to associate existing)"
    )
    file_uri: Optional[str] = Field(
        default=None,
        description="URI to file: file:// for local files, http(s):// for URLs (use this OR file_data)"
    )
    file_id: Optional[int] = Field(
        default=None,
        description="Existing file ID to associate with listing (use instead of uploading new file)"
    )
    rank: Optional[int] = Field(
        default=None,
        description="Position of file in listing"
    )


class DeleteListingFileParams(BaseModel):
    """Parameters for etspi_delete_listing_file tool"""
    shop_id: int = Field(
        description="The Etsy shop ID"
    )
    listing_id: int = Field(
        description="The listing ID"
    )
    file_id: int = Field(
        description="The file ID to delete"
    )
    confirm: Optional[bool] = Field(
        default=False,
        description="Set to true to skip confirmation prompt"
    )


# ============================================================================
# Property Management Tools
# ============================================================================

class GetListingPropertiesParams(BaseModel):
    """Parameters for etspi_get_listing_properties tool"""
    shop_id: int = Field(
        description="The Etsy shop ID"
    )
    listing_id: int = Field(
        description="The listing ID to get properties for"
    )
    property_id: Optional[int] = Field(
        default=None,
        description="Specific property ID to retrieve (optional)"
    )
    format_as_update: Optional[bool] = Field(
        default=False,
        description="Transform response to update property format"
    )
    query: Optional[str] = Field(
        default=None,
        description="JMESPath query to filter/transform the response"
    )


class UpdateListingPropertyParams(BaseModel):
    """Parameters for etspi_update_listing_property tool"""
    shop_id: int = Field(
        description="The Etsy shop ID"
    )
    listing_id: int = Field(
        description="The listing ID"
    )
    property_id: int = Field(
        description="The property ID to update"
    )
    property_data: Dict[str, Any] = Field(
        description="JSON object containing property details including value_ids, values, and scale_id"
    )
