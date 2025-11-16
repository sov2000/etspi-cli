"""
Media management tools for ETSPI MCP server (images, videos, files)
"""
from mcp.types import Tool, TextContent
from ..schemas import (
    GetListingImagesParams,
    UploadListingImageParams,
    DeleteListingImageParams,
    GetListingVideosParams,
    UploadListingVideoParams,
    DeleteListingVideoParams,
    GetListingFilesParams,
    UploadListingFileParams,
    DeleteListingFileParams
)
from ..utils import (
    apply_jmespath_query,
    format_success_response,
    format_error_response,
    to_json_string,
    decode_file_data
)
from etspi.etsyv3.models.file_request import (
    UploadListingImageRequest,
    UploadListingVideoRequest,
    UploadListingFileRequest
)


# Tool definitions
TOOLS = [
    # Image tools
    Tool(
        name="etspi_get_listing_images",
        description=(
            "Get all images or a specific image for a listing. "
            "Returns image IDs, URLs, ranks, and metadata. "
            "Supports JMESPath queries for filtering."
        ),
        inputSchema=GetListingImagesParams.model_json_schema()
    ),
    Tool(
        name="etspi_upload_listing_image",
        description=(
            "Upload a new image to a listing or update an existing one. "
            "Provide image via base64-encoded data or URI (file://, http://, https://). "
            "Can set rank (position), alt text, watermark, and overwrite options."
        ),
        inputSchema=UploadListingImageParams.model_json_schema()
    ),
    Tool(
        name="etspi_delete_listing_image",
        description=(
            "Delete an image from a listing. "
            "Requires image_id. Set confirm=true to skip confirmation."
        ),
        inputSchema=DeleteListingImageParams.model_json_schema()
    ),
    # Video tools
    Tool(
        name="etspi_get_listing_videos",
        description=(
            "Get all videos or a specific video for a listing. "
            "Returns video IDs, URLs, and metadata. "
            "Supports JMESPath queries for filtering."
        ),
        inputSchema=GetListingVideosParams.model_json_schema()
    ),
    Tool(
        name="etspi_upload_listing_video",
        description=(
            "Upload a new video to a listing or update an existing one. "
            "Provide video via base64-encoded data or URI (file://, http://, https://)."
        ),
        inputSchema=UploadListingVideoParams.model_json_schema()
    ),
    Tool(
        name="etspi_delete_listing_video",
        description=(
            "Delete a video from a listing. "
            "Requires video_id. Set confirm=true to skip confirmation."
        ),
        inputSchema=DeleteListingVideoParams.model_json_schema()
    ),
    # File tools
    Tool(
        name="etspi_get_listing_files",
        description=(
            "Get digital files associated with a listing. "
            "Returns file IDs, names, sizes, and metadata. "
            "Supports JMESPath queries for filtering."
        ),
        inputSchema=GetListingFilesParams.model_json_schema()
    ),
    Tool(
        name="etspi_upload_listing_file",
        description=(
            "Upload a digital file to a listing or associate an existing file. "
            "Provide file via base64-encoded data, URI, or existing file_id. "
            "Can set rank (position in file list)."
        ),
        inputSchema=UploadListingFileParams.model_json_schema()
    ),
    Tool(
        name="etspi_delete_listing_file",
        description=(
            "Delete a digital file from a listing. "
            "Requires file_id. Set confirm=true to skip confirmation."
        ),
        inputSchema=DeleteListingFileParams.model_json_schema()
    )
]


# ============================================================================
# Image Handlers
# ============================================================================

async def handle_get_listing_images(etsy_api, arguments: dict) -> list:
    """Handle etspi_get_listing_images tool call"""
    params = GetListingImagesParams(**arguments)

    try:
        if params.image_id:
            result = etsy_api.get_listing_image(
                listing_id=params.listing_id,
                image_id=params.image_id
            )
        else:
            result = etsy_api.get_listing_images(listing_id=params.listing_id)

        if params.query:
            result = apply_jmespath_query(result, params.query)

        response = format_success_response(result)
        return [TextContent(type="text", text=to_json_string(response))]

    except Exception as ex:
        response = format_error_response(ex)
        return [TextContent(type="text", text=to_json_string(response))]


async def handle_upload_listing_image(etsy_api, arguments: dict) -> list:
    """Handle etspi_upload_listing_image tool call"""
    params = UploadListingImageParams(**arguments)

    try:
        # Decode image data
        image_bytes = decode_file_data(params.image_data, params.image_uri)

        if not image_bytes:
            raise ValueError("Must provide either image_data or image_uri")

        # Create upload request
        upload_request = UploadListingImageRequest(
            image=image_bytes,
            rank=params.rank,
            overwrite=params.overwrite,
            is_watermarked=params.watermark,
            alt_text=params.alt_text
        )

        # Upload or update image
        if params.image_id:
            # Update existing image
            upload_request.image_id = params.image_id
            result = etsy_api.update_listing_image_id(
                shop_id=params.shop_id,
                listing_id=params.listing_id,
                image=upload_request
            )
        else:
            # Upload new image
            result = etsy_api.upload_listing_image(
                shop_id=params.shop_id,
                listing_id=params.listing_id,
                image=upload_request
            )

        response = format_success_response(result)
        return [TextContent(type="text", text=to_json_string(response))]

    except Exception as ex:
        response = format_error_response(ex)
        return [TextContent(type="text", text=to_json_string(response))]


async def handle_delete_listing_image(etsy_api, arguments: dict) -> list:
    """Handle etspi_delete_listing_image tool call"""
    params = DeleteListingImageParams(**arguments)

    try:
        if not params.confirm:
            return [TextContent(
                type="text",
                text=to_json_string({
                    "success": False,
                    "error": {
                        "type": "ConfirmationRequired",
                        "message": "Set confirm=true to delete this image."
                    }
                })
            )]

        result = etsy_api.delete_listing_image(
            listing_id=params.listing_id,
            image_id=params.image_id
        )

        response = format_success_response({
            "listing_id": params.listing_id,
            "image_id": params.image_id,
            "deleted": True,
            "message": "Image deleted successfully"
        })
        return [TextContent(type="text", text=to_json_string(response))]

    except Exception as ex:
        response = format_error_response(ex)
        return [TextContent(type="text", text=to_json_string(response))]


# ============================================================================
# Video Handlers
# ============================================================================

async def handle_get_listing_videos(etsy_api, arguments: dict) -> list:
    """Handle etspi_get_listing_videos tool call"""
    params = GetListingVideosParams(**arguments)

    try:
        if params.video_id:
            result = etsy_api.get_listing_video(
                listing_id=params.listing_id,
                video_id=params.video_id
            )
        else:
            result = etsy_api.get_listing_videos(listing_id=params.listing_id)

        if params.query:
            result = apply_jmespath_query(result, params.query)

        response = format_success_response(result)
        return [TextContent(type="text", text=to_json_string(response))]

    except Exception as ex:
        response = format_error_response(ex)
        return [TextContent(type="text", text=to_json_string(response))]


async def handle_upload_listing_video(etsy_api, arguments: dict) -> list:
    """Handle etspi_upload_listing_video tool call"""
    params = UploadListingVideoParams(**arguments)

    try:
        # Decode video data
        video_bytes = decode_file_data(params.video_data, params.video_uri)

        if not video_bytes:
            raise ValueError("Must provide either video_data or video_uri")

        # Create upload request
        upload_request = UploadListingVideoRequest(video=video_bytes)

        if params.video_id:
            upload_request.video_id = params.video_id

        # Upload video
        result = etsy_api.upload_listing_video(
            shop_id=params.shop_id,
            listing_id=params.listing_id,
            video=upload_request
        )

        response = format_success_response(result)
        return [TextContent(type="text", text=to_json_string(response))]

    except Exception as ex:
        response = format_error_response(ex)
        return [TextContent(type="text", text=to_json_string(response))]


async def handle_delete_listing_video(etsy_api, arguments: dict) -> list:
    """Handle etspi_delete_listing_video tool call"""
    params = DeleteListingVideoParams(**arguments)

    try:
        if not params.confirm:
            return [TextContent(
                type="text",
                text=to_json_string({
                    "success": False,
                    "error": {
                        "type": "ConfirmationRequired",
                        "message": "Set confirm=true to delete this video."
                    }
                })
            )]

        result = etsy_api.delete_listing_video(
            listing_id=params.listing_id,
            video_id=params.video_id
        )

        response = format_success_response({
            "listing_id": params.listing_id,
            "video_id": params.video_id,
            "deleted": True,
            "message": "Video deleted successfully"
        })
        return [TextContent(type="text", text=to_json_string(response))]

    except Exception as ex:
        response = format_error_response(ex)
        return [TextContent(type="text", text=to_json_string(response))]


# ============================================================================
# File Handlers (Digital Products)
# ============================================================================

async def handle_get_listing_files(etsy_api, arguments: dict) -> list:
    """Handle etspi_get_listing_files tool call"""
    params = GetListingFilesParams(**arguments)

    try:
        if params.file_id:
            result = etsy_api.get_listing_file(
                listing_id=params.listing_id,
                file_id=params.file_id
            )
        else:
            result = etsy_api.get_all_listing_files(
                shop_id=params.shop_id,
                listing_id=params.listing_id
            )

        if params.query:
            result = apply_jmespath_query(result, params.query)

        response = format_success_response(result)
        return [TextContent(type="text", text=to_json_string(response))]

    except Exception as ex:
        response = format_error_response(ex)
        return [TextContent(type="text", text=to_json_string(response))]


async def handle_upload_listing_file(etsy_api, arguments: dict) -> list:
    """Handle etspi_upload_listing_file tool call"""
    params = UploadListingFileParams(**arguments)

    try:
        # Decode file data
        file_bytes = decode_file_data(params.file_data, params.file_uri)

        # Create upload request
        upload_request = UploadListingFileRequest(
            file=file_bytes if file_bytes else None,
            listing_file_id=params.file_id,
            rank=params.rank
        )

        # Upload file
        result = etsy_api.upload_listing_file(
            shop_id=params.shop_id,
            listing_id=params.listing_id,
            file=upload_request
        )

        response = format_success_response(result)
        return [TextContent(type="text", text=to_json_string(response))]

    except Exception as ex:
        response = format_error_response(ex)
        return [TextContent(type="text", text=to_json_string(response))]


async def handle_delete_listing_file(etsy_api, arguments: dict) -> list:
    """Handle etspi_delete_listing_file tool call"""
    params = DeleteListingFileParams(**arguments)

    try:
        if not params.confirm:
            return [TextContent(
                type="text",
                text=to_json_string({
                    "success": False,
                    "error": {
                        "type": "ConfirmationRequired",
                        "message": "Set confirm=true to delete this file."
                    }
                })
            )]

        result = etsy_api.delete_listing_file(
            listing_id=params.listing_id,
            file_id=params.file_id
        )

        response = format_success_response({
            "listing_id": params.listing_id,
            "file_id": params.file_id,
            "deleted": True,
            "message": "File deleted successfully"
        })
        return [TextContent(type="text", text=to_json_string(response))]

    except Exception as ex:
        response = format_error_response(ex)
        return [TextContent(type="text", text=to_json_string(response))]


# ============================================================================
# Tool Call Router
# ============================================================================

async def handle_tool_call(tool_name: str, etsy_api, arguments: dict) -> list:
    """Route tool calls to appropriate handler"""
    handlers = {
        "etspi_get_listing_images": handle_get_listing_images,
        "etspi_upload_listing_image": handle_upload_listing_image,
        "etspi_delete_listing_image": handle_delete_listing_image,
        "etspi_get_listing_videos": handle_get_listing_videos,
        "etspi_upload_listing_video": handle_upload_listing_video,
        "etspi_delete_listing_video": handle_delete_listing_video,
        "etspi_get_listing_files": handle_get_listing_files,
        "etspi_upload_listing_file": handle_upload_listing_file,
        "etspi_delete_listing_file": handle_delete_listing_file,
    }

    handler = handlers.get(tool_name)
    if handler:
        return await handler(etsy_api, arguments)

    return [TextContent(
        type="text",
        text=to_json_string(format_error_response(
            ValueError(f"Unknown tool: {tool_name}")
        ))
    )]
