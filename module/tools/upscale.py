from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.download_util import load_file_from_url
import numpy as np
from torch import nn as nn
from PIL import Image

from dataclasses import dataclass, field
import os
from enum import Enum,auto as enumauto

from module import Data

class ModelType(Enum):
    R_ESRGAN_2X = enumauto()
    R_ESRGAN_4X = enumauto()
    R_ESRNET_4X = enumauto()
    R_ESRGAN_ANIME6B_4X = enumauto()
    CUSTOM = enumauto()
    
@dataclass
class UpcaleOption:
    force_download: bool = field(default=False)
    model_type: ModelType = field(default=ModelType.R_ESRGAN_ANIME6B_4X)
    model_path: str = field(default="./models/real_esrgan")
    custom_model_name:str = field(default="")
    custom_model:nn.Module = field(default=None)
    custom_scale:int = field(default=2)
    tile:int = field(default=512)
    tile_pad:int = field(default=10)
    pre_pad:int = field(default=10)
    half:bool = field(default=False)

class CustomModelError(RuntimeError): ...

class UpscaleModel(RealESRGANer):
    def __init__(self,option:UpcaleOption|None=UpcaleOption()):
        match option.model_type.value:
            case ModelType.R_ESRGAN_2X.value:
                url='https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth'
                file="RealESRGAN_x2plus.pth"
                model=RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
                scale=2
            case ModelType.R_ESRGAN_4X.value:
                url='https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
                file="RealESRGAN_x4plus.pth"
                model=RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
                scale=4
            case ModelType.R_ESRNET_4X.value:
                url="'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRNet_x4plus.pth'"
                file="RealESRNet_x4plus.pth"
                scale=8
                model=RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
            case ModelType.R_ESRGAN_ANIME6B_4X.value:
                url="https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"
                file="RealESRGAN_x4plus_anime_6B.pth"
                model=RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
                scale=4
            case ModelType.CUSTOM.value:
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
                model_path = load_file_from_url(
                    url=url, model_dir=option.model_path, progress=True, file_name=None)
        model_path = os.path.join(option.model_path,file)
        dni_weight=None
        tile=option.tile
        tile_pad=option.tile_pad
        pre_pad=option.pre_pad
        half=option.half
        device=None
        super().__init__(scale, model_path, dni_weight, model, tile, tile_pad, pre_pad, half, device)

    def upscale_data(self,data:Data)->Image:
        np_img = np.array(data.img)
        img,_ = super().enhance(np_img)
        img = Image.fromarray(img)
        return img