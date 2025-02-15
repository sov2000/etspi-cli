import json
import yaml
import hashlib
import time

from typing import Any, Dict, List, Optional

class SyncOperation:
    def __init__(self, src_file: str = None, operation: str = None, params: Dict = None):
        self.src_file = src_file
        self.operation = operation
        self.params = params

    def to_dict(self) -> Dict:
        return { "src_file": self.src_file, "operation": self.operation, "params": self.params }

class Listing:
    def __init__(self, id: int, listing: Dict, images: List = None, meta: Dict = None):
        self.images = images
        self.listing = listing
        self.meta = ListingMeta(listing_id=id).to_dict()
    
    def to_dict(self) -> Dict:
        id = self.meta.get("listing_id", 0)
        meta = ListingMeta(listing_id=id)
        if self.images:
            meta.images_hash = hash_list_data(self.images)
        if self.listing:
            meta.listing_hash = hash_list_data(self.listing)
        self.meta = meta.to_dict()
        return { "images": self.images, "listing": self.listing, "meta": self.meta }

class ListingMeta:
    def __init__(self, listing_id: int = 0, listing_hash: str = None, images_hash: str = None):
        self.listing_id = listing_id
        self.images_hash = images_hash
        self.listing_hash = listing_hash
        self.last_updated = int(time.time())

    def to_dict(self) -> Dict:
        return { "listing_id": self.listing_id, "images_hash": self.images_hash, "listing_hash": self.listing_hash, 
                "last_updated": self.last_updated }

def hash_list_data(obj: Any) -> Optional[str]:
    json_string = json.dumps(obj, ensure_ascii=False) # ensure_ascii is important for non-ascii characters in the dictionary
    encoded_string = json_string.encode('utf-8')
    hash_object = hashlib.sha256(encoded_string)
    hex_digest = hash_object.hexdigest()
    return hex_digest
