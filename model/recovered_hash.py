from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class RecoveredHashCreate(BaseModel):
    """Model for creating a recovered hash entry"""
    hash: str = Field(..., description="The hash value that was cracked")
    plaintext: str = Field(..., description="The plaintext value for the hash")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata about the recovered hash")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "hash": "5f4dcc3b5aa765d61d8327deb882cf99",
                    "plaintext": "password",
                    "metadata": {"time_to_crack": 12.5}
                }
            ]
        }
    }
