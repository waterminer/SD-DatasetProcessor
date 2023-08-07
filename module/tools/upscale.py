from huggingface_hub import hf_hub_download
import numpy as np
import cv2
import realesrgan

from dataclasses import dataclass, field
import os
from enum import Enum

from module import data

class ModelType(Enum):
    R_ESRGEN_2X = "R_ESRGEN_2X"
    R_ESRGEN_4X = ""
    R_ESRGEN_8X = ""
    CUSTOM=""
    
@dataclass
class UpcaleOption:
    force_download: bool = field(default=False)
    model_type: ModelType = field(default=ModelType.R_ESRGEN)
    model_path: str = field(default="./models")
    custom_model_name:str = field(default="")

class UpscaleModel:
    def __init__(self,option:UpcaleOption):
        match option.model_type:
            
        hf_hub_download(
            self.repo_id
        )