from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from etspi.etsyv3.enums import (
    ItemDimensionsUnit,
    ItemWeightUnit,
    ListingRequestState,
    ListingType,
    WhenMade,
    WhoMade,
)
from etspi.etsyv3.models.product import Product
from etspi.etsyv3.util import todict


class Request:
    def __init__(
        self,
        nullable: Optional[List[str]] = None,
        mandatory: Optional[List[str]] = None,
    ):
        self._nullable = nullable if nullable is not None else []
        self._mandatory = mandatory if mandatory is not None else []
        if not self.check_mandatory():
            raise ValueError

    def check_mandatory(self) -> bool:
        if self._mandatory is not None:
            for key in self._mandatory:
                try:
                    if self.__dict__[key] is None:
                        return False
                except Exception:
                    return False
        return True

    def get_nulled(self) -> List[str]:
        return [
            key
            for key, value in self.__dict__.items()
            if key in self._nullable and (value == [] or value == "" or value == 0)
        ]

    def get_dict(self) -> Any:
        nulled = self.get_nulled()
        return todict(self, nullable=nulled)


class CreateDraftListingRequest(Request):
    nullable = [
        "shipping_profile_id",
        "return_policy_id",
        "materials",
        "shop_section_id",
        "processing_min",
        "processing_max",
        "tags",
        "styles",
        "item_weight",
        "item_length",
        "item_width",
        "item_height",
        "item_weight_unit",
        "item_dimensions_unit",
        "production_partner_ids",
        "image_ids",
    ]
    mandatory = [
        "quantity",
        "title",
        "description",
        "price",
        "who_made",
        "when_made",
        "taxonomy_id",
    ]

    def __init__(
        self,
        quantity: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        who_made: Optional[WhoMade] = None,
        when_made: Optional[WhenMade] = None,
        taxonomy_id: Optional[int] = None,
        shipping_profile_id: Optional[int] = None,
        return_policy_id: Optional[int] = None,
        materials: Optional[List[str]] = None,
        shop_section_id: Optional[int] = None,
        processing_min: Optional[int] = None,
        processing_max: Optional[int] = None,
        tags: Optional[List[str]] = None,
        styles: Optional[List[str]] = None,
        item_weight: Optional[float] = None,
        item_length: Optional[float] = None,
        item_width: Optional[float] = None,
        item_height: Optional[float] = None,
        item_weight_unit: Optional[ItemWeightUnit] = None,
        item_dimensions_unit: Optional[ItemDimensionsUnit] = None,
        is_personalizable: Optional[bool] = None,
        personalization_is_required: Optional[bool] = None,
        personalization_char_count_max: Optional[int] = None,
        personalization_instructions: Optional[str] = None,
        production_partner_ids: Optional[int] = None,
        image_ids: Optional[List[int]] = None,
        is_supply: Optional[bool] = None,
        is_customizable: Optional[bool] = None,
        should_auto_renew: Optional[bool] = None,
        is_taxable: Optional[bool] = None,
        listing_type: Optional[ListingType] = None,
    ):
        self.quantity = quantity
        self.title = title
        self.description = description
        self.price = price
        self.who_made = who_made
        self.when_made = when_made
        self.taxonomy_id = taxonomy_id
        self.shipping_profile_id = shipping_profile_id
        self.return_policy_id = return_policy_id
        self.materials = materials
        self.shop_section_id = shop_section_id
        self.processing_min = processing_min
        self.processing_max = processing_max
        self.tags = tags
        self.styles = styles
        self.item_weight = item_weight
        self.item_length = item_length
        self.item_width = item_width
        self.item_height = item_height
        self.item_weight_unit = item_weight_unit
        self.item_dimensions_unit = item_dimensions_unit
        self.is_personalizable = is_personalizable
        self.personalization_is_required = personalization_is_required
        self.personalization_char_count_max = personalization_char_count_max
        self.personalization_instructions = personalization_instructions
        self.production_partner_ids = production_partner_ids
        self.image_ids = image_ids
        self.is_supply = is_supply
        self.is_customizable = is_customizable
        self.should_auto_renew = should_auto_renew
        self.is_taxable = is_taxable
        self.listing_type = listing_type
        super().__init__(
            nullable=CreateDraftListingRequest.nullable,
            mandatory=CreateDraftListingRequest.mandatory,
        )

    @staticmethod
    def generate_request_from_listing_response(
        response: Dict[str, Any]
    ) -> CreateDraftListingRequest:
        imgs = [i["listing_image_id"] for i in response["images"]] if response.get("images") is not None else None
        schp = response["shipping_profile"]["shipping_profile_id"] if response.get("shipping_profile") is not None else None
        prdp = [p["production_partner_id"] for p in response["production_partners"]] if response.get("production_partners") is not None else None
        return CreateDraftListingRequest(
            quantity = response["quantity"],
            title = response["title"],
            description = response["description"],
            price = response["price"]["amount"] / response["price"]["divisor"],
            who_made = WhoMade(response["who_made"]),
            when_made = WhenMade(response["when_made"]),
            taxonomy_id = response["taxonomy_id"],
            shipping_profile_id = schp,
            return_policy_id = response["return_policy_id"],
            materials = response["materials"],
            shop_section_id = response["shop_section_id"],
            processing_min = response["processing_min"],
            processing_max = response["processing_max"],
            tags = response["tags"],
            styles = response["style"],
            item_weight = response["item_weight"],
            item_length = response["item_length"],
            item_width = response["item_width"],
            item_height = response["item_height"],
            item_weight_unit = response["item_weight_unit"],
            item_dimensions_unit = response["item_dimensions_unit"],
            is_personalizable = response["is_personalizable"],
            personalization_is_required = response["personalization_is_required"],
            personalization_char_count_max = response["personalization_char_count_max"],
            personalization_instructions = response["personalization_instructions"],
            production_partner_ids = prdp,
            image_ids = imgs,
            is_supply = response["is_supply"],
            is_customizable = response["is_customizable"],
            should_auto_renew = response["should_auto_renew"],
            is_taxable = response["is_taxable"],
            listing_type = response["listing_type"]
        )

class CreateListingTranslationRequest(Request):
    nullable: List[str] = [
        "tags"
    ]
    mandatory: List[str] = [
        "title",
        "description"
    ]

    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        self.title = title
        self.description = description
        self.tags = tags
        super().__init__(
            nullable=CreateListingTranslationRequest.nullable,
            mandatory=CreateListingTranslationRequest.mandatory,
        )


class UpdateListingRequest(Request):
    nullable: List[str] = [
        "materials",
        "shipping_profile_id",
        "shop_section_id",
        "item_weight",
        "item_length",
        "item_width",
        "item_height",
        "item_weight_unit",
        "item_dimensions_unit",
        "tags",
        "featured_rank",
        "production_partner_ids",
        "type",
    ]

    mandatory: List[str] = []

    def __init__(
        self,
        image_ids: Optional[List[str]] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        materials: Optional[List[str]] = None,
        should_auto_renew: Optional[bool] = None,
        shipping_profile_id: Optional[int] = None,
        return_policy_id: Optional[int] = None,
        shop_section_id: Optional[int] = None,
        item_weight: Optional[float] = None,
        item_length: Optional[float] = None,
        item_width: Optional[float] = None,
        item_height: Optional[float] = None,
        item_weight_unit: Optional[ItemWeightUnit] = None,
        item_dimensions_unit: Optional[ItemDimensionsUnit] = None,
        is_taxable: Optional[bool] = None,
        taxonomy_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
        who_made: Optional[WhoMade] = None,
        when_made: Optional[WhenMade] = None,
        featured_rank: Optional[int] = None,
        is_personalizable: Optional[bool] = None,
        personalization_is_required: Optional[bool] = None,
        personalization_char_count_max: Optional[int] = None,
        personalization_instructions: Optional[str] = None,
        state: Optional[ListingRequestState] = None,
        is_supply: Optional[bool] = None,
        production_partner_ids: Optional[List[int]] = None,
        listing_type: Optional[ListingType] = None,
    ):
        self.image_ids = image_ids
        self.title = title
        self.description = description
        self.materials = materials
        self.should_auto_renew = should_auto_renew
        self.shipping_profile_id = shipping_profile_id
        self.return_policy_id = return_policy_id
        self.shop_section_id = shop_section_id
        self.item_weight = item_weight
        self.item_length = item_length
        self.item_width = item_width
        self.item_height = item_height
        self.item_weight_unit = item_weight_unit
        self.item_dimensions_unit = item_dimensions_unit
        self.is_taxable = is_taxable
        self.taxonomy_id = taxonomy_id
        self.tags = tags
        self.who_made = who_made
        self.when_made = when_made
        self.featured_rank = featured_rank
        self.is_personalizable = is_personalizable
        self.personalization_is_required = personalization_is_required
        self.personalization_char_count_max = personalization_char_count_max
        self.personalization_instructions = personalization_instructions
        self.state = state
        self.is_supply = is_supply
        self.production_partner_ids = production_partner_ids
        self.listing_type = listing_type
        super().__init__(nullable=UpdateListingRequest.nullable)

    @staticmethod
    def generate_request_from_listing_response(
        response: Dict[str, Any]
    ) -> UpdateListingRequest:
        imgs = [i["listing_image_id"] for i in response["images"]] if response.get("images") is not None else None
        schp = response["shipping_profile"]["shipping_profile_id"] if response.get("shipping_profile") is not None else None
        prdp = [p["production_partner_id"] for p in response["production_partners"]] if response.get("production_partners") is not None else None
        return UpdateListingRequest(
            image_ids=imgs,
            title=response["title"],
            description=response["description"],
            materials=response["materials"],
            should_auto_renew=response["should_auto_renew"],
            shipping_profile_id=schp,
            return_policy_id=response["return_policy_id"],
            shop_section_id=response["shop_section_id"],
            item_weight=response["item_weight"],
            item_length=response["item_length"],
            item_width=response["item_width"],
            item_height=response["item_height"],
            item_weight_unit=response["item_weight_unit"],
            item_dimensions_unit=response["item_dimensions_unit"],
            is_taxable=response["is_taxable"],
            taxonomy_id=response["taxonomy_id"],
            tags=response["tags"],
            who_made=response["who_made"],
            when_made=response["when_made"],
            featured_rank=response["featured_rank"],
            is_personalizable=response["is_personalizable"],
            personalization_is_required=response["personalization_is_required"],
            personalization_char_count_max=response["personalization_char_count_max"],
            personalization_instructions=response["personalization_instructions"],
            state=response["state"],
            is_supply=response["is_supply"],
            production_partner_ids=prdp,
            listing_type=response["listing_type"]
        )


class UpdateListingInventoryRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = ["products"]

    def __init__(
        self,
        products: List[Product],
        price_on_property: Optional[List[int]] = None,
        quantity_on_property: Optional[List[int]] = None,
        sku_on_property: Optional[List[int]] = None,
    ):
        self.products = products
        self.price_on_property = price_on_property
        self.quantity_on_property = quantity_on_property
        self.sku_on_property = sku_on_property
        super().__init__(
            nullable=UpdateListingInventoryRequest.nullable,
            mandatory=UpdateListingInventoryRequest.mandatory,
        )

    @staticmethod
    def generate_request_from_inventory_response(
        response: Dict[str, Any]
    ) -> UpdateListingInventoryRequest:
        products = []
        for product in response["products"]:
            property_values = product["property_values"]
            for prop_val in property_values:
                prop_val.pop("scale_name", None)
                prop_val.pop("value_pairs", None)
            offerings = product["offerings"]
            for offering in offerings:
                offering.pop("is_deleted", None)
                offering.pop("offering_id", None)
                offering["price"] = (
                    offering["price"]["amount"] / offering["price"]["divisor"]
                )
            products.append(Product(product["sku"], property_values, offerings))
        price_on_property = response["price_on_property"]
        quantity_on_property = response["quantity_on_property"]
        sku_on_property = response["sku_on_property"]
        return UpdateListingInventoryRequest(
            products, price_on_property, quantity_on_property, sku_on_property
        )


class UpdateVariationImagesRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = []

    def __init__(self, variation_images: List[Dict[str, Any]]) -> None:
        self.variation_images = variation_images
        super().__init__(
            nullable=UpdateVariationImagesRequest.nullable,
            mandatory=UpdateVariationImagesRequest.mandatory,
        )

    @staticmethod
    def generate_request_from_variation_images_response(
        response: Dict[str, Any]
    ) -> UpdateVariationImagesRequest:
        variation_images = response["results"]
        for variation_image in variation_images:
            variation_image.pop("value", None)
        return UpdateVariationImagesRequest(variation_images)

class UpdateListingImageIDRequest(Request):
    nullable: List[str] = []
    mandatory: List[str] = ["listing_image_id"]

    def __init__(
        self,
        listing_image_id: int,
        rank: Optional[int] = None,
        overwrite: Optional[bool] = None,
        is_watermarked: Optional[bool] = None,
        alt_text: Optional[str] = None,
    ) -> None:

        self.listing_image_id = listing_image_id
        self.rank = rank
        self.overwrite = overwrite
        self.is_watermarked = is_watermarked
        self.alt_text = alt_text

        super().__init__(
            nullable=UpdateListingImageIDRequest.nullable,
            mandatory=UpdateListingImageIDRequest.mandatory,
        )


class UpdateListingPropertyRequest(Request):
    nullable: List[str] = []

    mandatory: List[str] = [
        "value_ids",
        "values",
    ]

    def __init__(
        self,
        value_ids: Optional[List[int]] = None,
        values: Optional[List[str]] = None,
        scale_id: Optional[int] = None,
    ):
        self.value_ids = value_ids
        self.values = values
        self.scale_id = scale_id
        super().__init__(
            nullable=UpdateListingPropertyRequest.nullable,
            mandatory=UpdateListingPropertyRequest.mandatory,
        )
    
    @staticmethod
    def generate_request_from_listing_property_response(
        response: Dict[str, Any]
    ) -> UpdateListingPropertyRequest:
        return UpdateListingPropertyRequest(
            value_ids = response["value_ids"],
            values = response["values"],
            scale_id = response["scale_id"],
        )

class UpdateListingTranslationRequest(Request):
    nullable: List[str] = [
        "tags"
    ]
    mandatory: List[str] = [
        "title",
        "description"
    ]

    def __init__(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        self.title = title
        self.description = description
        self.tags = tags
        super().__init__(
            nullable=UpdateListingTranslationRequest.nullable,
            mandatory=UpdateListingTranslationRequest.mandatory,
        )