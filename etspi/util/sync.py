import json
import yaml
import hashlib
import time

from typing import Any, Dict, List, Optional
from etspi.etsyv3.models import UpdateListingImageIDRequest

class SyncOperation:
    def __init__(self, src_file: str = None, operation: str = None, params: Dict = None):
        self.src_file = src_file
        self.operation = operation
        self.params = params

    def to_dict(self) -> Dict:
        return { "src_file": self.src_file, "operation": self.operation, "params": self.params }

class Listing:
    def __init__(self, id: int, listing: Dict, images: List = None, inventory: List = None, properties: List = None, meta: Dict = None):
        self.images = images
        self.listing = listing
        self.inventory = inventory
        self.properties = properties
        self.meta = ListingMeta(listing_id=id).to_dict()
    
    def to_dict(self) -> Dict:
        id = self.meta.get("listing_id", 0)
        meta = ListingMeta(listing_id=id)
        if self.images:
            meta.images_hash = hash_list_data(self.images)
            meta.images_item_hashes = [hash_list_data(img) for img in self.images]
        if self.inventory:
            meta.inventory_hash = hash_list_data(self.inventory)
        if self.properties:
            meta.properties_hash = hash_list_data(self.properties)
            meta.properties_item_hashes = [hash_list_data(prp) for prp in self.properties]
        if self.listing:
            meta.listing_hash = hash_list_data(self.listing)
        self.meta = meta.to_dict()
        return { "listing": self.listing, "images": self.images, "inventory": self.inventory, 
                "properties": self.properties, "meta": self.meta }

class ListingMeta:
    def __init__(self, listing_id: int = 0, listing_hash: str = None, images_hash: str = None,
                 images_item_hashes: List = None, inventory_hash: str = None, properties_hash: str = None,
                 properties_item_hashes: List = None):
        self.listing_id = listing_id
        self.images_hash = images_hash
        self.images_item_hashes = images_item_hashes
        self.inventory_hash = inventory_hash
        self.properties_hash = properties_hash
        self.properties_item_hashes = properties_item_hashes
        self.listing_hash = listing_hash
        self.last_updated = int(time.time())

    def to_dict(self) -> Dict:
        return { "listing_id": self.listing_id, "images_hash": self.images_hash, "images_item_hashes": self.images_item_hashes,
                "inventory_hash": self.inventory_hash, "properties_hash": self.properties_hash, "properties_item_hashes": self.properties_item_hashes,
                "listing_hash": self.listing_hash, "last_updated": self.last_updated }
    
class ListingImageRequest(UpdateListingImageIDRequest):
    def __init__(self, listing_image_id: int, rank: int, url: str = None, alt_text: str = None):
        super().__init__(listing_image_id=listing_image_id, rank=rank, alt_text=alt_text)
        self.url = url
    
    def to_dict(self) -> Dict:
        return { "image_id": self.listing_image_id, "rank": self.rank, "url": self.url, "alt_text": self.alt_text }
    
    @staticmethod
    def generate_request_from_image_response(obj: Dict) -> Any:
        return ListingImageRequest(listing_image_id=obj.get("listing_image_id", 0), rank=obj.get("rank", 0), 
                                   url=obj.get("url_fullxfull", ""), alt_text=obj.get("alt_text", ""))

def hash_list_data(obj: Any) -> Optional[str]:
    json_string = json.dumps(obj, ensure_ascii=False) # ensure_ascii is important for non-ascii characters in the dictionary
    encoded_string = json_string.encode('utf-8')
    hash_object = hashlib.sha256(encoded_string)
    hex_digest = hash_object.hexdigest()
    return hex_digest
