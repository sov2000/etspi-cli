import json
import yaml
import hashlib
import os
import glob

from typing import Any, Dict, List, Optional

class SyncOperation:
    def __init__(self, src_file: str = None, operation: str = None, params: Dict = None) -> None:
        self.src_file = src_file
        self.operation = operation
        self.params = params

def hash_list_data(obj: Any) -> Optional[str]:
    json_string = json.dumps(obj, ensure_ascii=False) # ensure_ascii is important for non-ascii characters in the dictionary
    encoded_string = json_string.encode('utf-8')
    hash_object = hashlib.sha256(encoded_string)
    hex_digest = hash_object.hexdigest()
    return hex_digest
