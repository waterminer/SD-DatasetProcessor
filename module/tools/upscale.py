from huggingface_hub import hf_hub_download
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
from torch import nn as nn

from dataclasses import dataclass, field
import os
from enum import Enum,auto as enumauto

from module import Data

class ModelType(Enum):
    R_ESRGAN_2X = enumauto()
    R_ESRGAN_4X = enumauto()
    R_ESRGAN_8X = enumauto()
    R_ESRGAN_ANIME6B_4X = enumauto()
    CUSTOM = enumauto()
    
@dataclass
class UpcaleOption:
    # downloadsorce:str = field(default="hugginface")
    force_download: bool = field(default=False)
    model_type: ModelType = field(default=ModelType.R_ESRGAN_2X)
    model_path: str = field(default="./models/real_esrgan")
    custom_model_name:str = field(default="")
    custom_model:nn.Module = field(default=None)
    custom_scale:int = field(default=2)
    tile:int = field(default=0)
    tile_pad:int = field(default=10)
    pre_pad:int = field(default=10)
    half:bool = field(default=False)

class CustomModelError(RuntimeError): ...

class UpscaleModel(RealESRGANer):
    def __init__(self,option:UpcaleOption|None=UpcaleOption()):
        match option.model_type.value:
            case ModelType.R_ESRGAN_2X.value:
                repo_id="ai-forever/Real-ESRGAN"
                file="RealESRGAN_x2.pth"
                model=RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
                scale=2
            case ModelType.R_ESRGAN_4X.value:
                repo_id="ai-forever/Real-ESRGAN"
                file="RealESRGAN_x4.pth"
                model=RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
                scale=4
            case ModelType.R_ESRGAN_8X.value:
                repo_id="ai-forever/Real-ESRGAN"
                file="RealESRGAN_x8.pth"
                scale=8
                model=RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=8)
            case ModelType.R_ESRGAN_ANIME_4X.value:
                repo_id="ximso/RealESRGAN_x4plus_anime_6B"
                file="RealESRGAN_x4plus_anime_6B.pth"
                model=RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
                scale=4
            case ModelType.CUSTOM.value:
                repo_id="custom"
                try:
                    file=option.custom_model_name
                    model=option.custom_model
                    scale=option.custom_scale
                    if not os.path.exists(os.path.join(option.model_path,file)):
                        raise ChildProcessError
                except CustomModelError:
                    print("UpcaleOption:custom_model is not exist!")
                    exit(1)
            case _:
                raise RuntimeError
                exit(1)
        print("Loading upscale model...")
        if option.model_type is not ModelType.CUSTOM.value and (
            not os.path.exists(os.path.join(option.model_path,file)) or option.force_download) :
            hf_hub_download(
                repo_id,
                file,
                cache_dir=option.model_path,
                force_download=True,
                force_filename=file
            )
        model_path = os.path.join(option.model_path,file)
        dni_weight=None,
        tile=option.tile,
        tile_pad=option.tile_pad,
        pre_pad=option.pre_pad,
        half=option.half,
        device=None,
        gpu_id=None
        super().__init__(scale, model_path, dni_weight, model, tile, tile_pad, pre_pad, half, device, gpu_id)