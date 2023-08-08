from huggingface_hub import hf_hub_download
import numpy as np
import cv2
import realesrgan

from dataclasses import dataclass, field
import os
from enum import Enum,auto as enumauto

from module import data

class ModelType(Enum):
    R_ESRGEN_2X = enumauto()
    R_ESRGEN_4X = enumauto()
    R_ESRGEN_8X = enumauto()
    CUSTOM=enumauto()
    
@dataclass
class UpcaleOption:
    force_download: bool = field(default=False)
    model_type: ModelType = field(default=ModelType.R_ESRGEN)
    model_path: str = field(default="./models")
    custom_model_name:str = field(default="")

class CustomModelError(RuntimeError): ...

class CustomModelNotExsitError(CustomModelError): ...

class UpscaleModel:
    def __init__(self,option:UpcaleOption):
        match option.model_type.value:
            case ModelType.R_ESRGEN_2X.value:
                self.repo_id="ai-forever/Real-ESRGAN"
                self.file="RealESRGAN_x2.pth"
                return
            case ModelType.R_ESRGEN_4X.value:
                self.repo_id="ai-forever/Real-ESRGAN"
                self.file="RealESRGAN_x4.pth"
            case ModelType.R_ESRGEN_8X.value:
                self.repo_id="ai-forever/Real-ESRGAN"
                self.file="RealESRGAN_x8.pth"
            case ModelType.CUSTOM.value:
                self.repo_id="custom"
                try:
                    self.file=option.custom_model_name
                except:
                    print("UpcaleOption:custom_model_name is not exist!")
                    exit(1)
            case _:
                raise RuntimeError
                exit(1)
        if option.model_type is not ModelType.CUSTOM.value and os.path.exists(os.path.join(option.model_path,self.file)):
            hf_hub_download(
                self.repo_id,
                self.file,
                force_download=True,
                force_filename=self.file
            )
        self.model = self.file