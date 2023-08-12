import numpy as np
from torch import nn as nn
from PIL.Image import Image, fromarray
from basicsr.archs.rrdbnet_arch import RRDBNet
from basicsr.utils.download_util import load_file_from_url
from huggingface_hub import hf_hub_download
from realesrgan import RealESRGANer as RealESRGANModel
from realcugan_ncnn_py import Realcugan as RealcuganModel

from dataclasses import dataclass, field
import os
from enum import Enum, auto as enumauto

from dataset_processor import Data


class ModelType(Enum):
    R_ESRGAN_2X = enumauto()
    R_ESRGAN_4X = enumauto()
    R_ESRNET_4X = enumauto()
    R_ESRGAN_ANIME6B_4X = enumauto()
    R_CUGAN_2X_CON = enumauto()
    R_CUGAN_2X_ND = enumauto()
    R_CUGAN_2X_D1 = enumauto()
    R_CUGAN_2X_D2 = enumauto()
    R_CUGAN_2X_D3 = enumauto()
    R_CUGAN_3X_CON = enumauto()
    R_CUGAN_3X_ND = enumauto()
    R_CUGAN_3X_D3 = enumauto()
    R_CUGAN_4X_CON = enumauto()
    R_CUGAN_4X_ND = enumauto()
    R_CUGAN_4X_D3 = enumauto()
    CUSTOM = enumauto()


@dataclass
class UpcaleOption:
    force_download: bool = field(default=False)
    model_type: ModelType = field(default=ModelType.R_ESRGAN_2X)
    model_path: str = field(default="./models")
    custom_model_name: str = field(default="")
    custom_model: nn.Module = field(default=None)
    custom_scale: int = field(default=2)
    tile: int = field(default=512)
    tile_pad: int = field(default=10)
    pre_pad: int = field(default=10)
    half: bool = field(default=True)
    gpuid: int = field(default=0)


class CustomModelError(RuntimeError): ...


class UpscaleModel():
    REAL_ESRGAN_MODEL = [
        ModelType.R_ESRGAN_2X,
        ModelType.R_ESRGAN_4X,
        ModelType.R_ESRNET_4X,
        ModelType.R_ESRGAN_ANIME6B_4X
    ]
    REAL_CUGAN_MODEL = [
        ModelType.R_CUGAN_2X_CON,
        ModelType.R_CUGAN_2X_ND,
        ModelType.R_CUGAN_2X_D1,
        ModelType.R_CUGAN_2X_D2,
        ModelType.R_CUGAN_2X_D3,
        ModelType.R_CUGAN_3X_CON,
        ModelType.R_CUGAN_3X_ND,
        ModelType.R_CUGAN_3X_D3,
        ModelType.R_CUGAN_4X_CON,
        ModelType.R_CUGAN_4X_ND,
        ModelType.R_CUGAN_4X_D3
    ]

    def __init__(self, option: UpcaleOption | None = UpcaleOption()):
        print("Init upscale...")
        self.realesrgan = None
        self.realcugan = None
        match option.model_type.value:
            case ModelType.R_ESRGAN_2X.value:
                url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth'
                file = "RealESRGAN_x2plus.pth"
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=2)
                scale = 2
            case ModelType.R_ESRGAN_4X.value:
                url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
                file = "RealESRGAN_x4plus.pth"
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
                scale = 4
            case ModelType.R_ESRNET_4X.value:
                url = "'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.1/RealESRNet_x4plus.pth'"
                file = "RealESRNet_x4plus.pth"
                scale = 8
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
            case ModelType.R_ESRGAN_ANIME6B_4X.value:
                url = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth"
                file = "RealESRGAN_x4plus_anime_6B.pth"
                model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=4)
                scale = 4
            case ModelType.R_CUGAN_2X_CON.value:
                model = "models-se"
                noise = -1
                scale = 2
            case ModelType.R_CUGAN_2X_ND.value:
                model = "models-se"
                noise = 0
                scale = 2
            case ModelType.R_CUGAN_2X_D1.value:
                model = "models-se"
                noise = 1
                scale = 2
            case ModelType.R_CUGAN_2X_D2.value:
                model = "models-se"
                noise = 2
                scale = 2
            case ModelType.R_CUGAN_2X_D3.value:
                model = "models-se"
                noise = 3
                scale = 2
            case ModelType.R_CUGAN_3X_CON.value:
                model = "models-se"
                noise = -1
                scale = 3
            case ModelType.R_CUGAN_3X_ND.value:
                model = "models-se"
                noise = 0
                scale = 3
            case ModelType.R_CUGAN_3X_D3.value:
                model = "models-se"
                noise = 3
                scale = 3
            case ModelType.R_CUGAN_4X_CON.value:
                model = "models-se"
                noise = -1
                scale = 4
            case ModelType.R_CUGAN_4X_ND.value:
                model = "models-se"
                noise = 0
                scale = 4
            case ModelType.R_CUGAN_4X_D3.value:
                model = "models-se"
                noise = 3
                scale = 4
            case ModelType.CUSTOM.value:
                try:
                    file = option.custom_model_name
                    model = option.custom_model
                    scale = option.custom_scale
                    if not os.path.exists(os.path.join(option.model_path, file)):
                        raise ChildProcessError
                except CustomModelError:
                    print("UpcaleOption:custom_model is not exist!")
                    exit(1)
            case _:
                raise RuntimeError
        print("Loading upscale model...")
        if option.model_type in self.REAL_ESRGAN_MODEL:  # 这是一个过度办法，将来我会把这些源换成从抱脸下载
            if os.path.exists(os.path.join(option.model_path, file)):
                model_path = os.path.join(option.model_path, file)
            else:
                model_path = os.path.join(option.model_path, "real_esrgan")
                if option.model_type is not ModelType.CUSTOM.value and (
                        not os.path.exists(os.path.join(model_path, file)) or option.force_download):
                    model_path = load_file_from_url(
                        url=url, model_dir=option.model_path, progress=True, file_name=None)
            tile = option.tile
            tile_pad = option.tile_pad
            pre_pad = option.pre_pad
            half = option.half
            gpuid = option.gpuid
            self.realesrgan = RealESRGANModel(
                scale=scale,
                model_path=model_path,
                model=model,
                tile=tile,
                tile_pad=tile_pad,
                pre_pad=pre_pad,
                half=half,
                gpu_id=gpuid)
        if option.model_type in self.REAL_CUGAN_MODEL:
            tile_size = option.tile
            gpuid = option.gpuid
            self.realcugan = RealcuganModel(gpuid, noise=noise, scale=scale, model=model, tilesize=tile_size)

    def upscale_data(self, data: Data) -> Image:
        if self.realesrgan:
            np_img = np.array(data.img)
            np_img, _ = self.realesrgan.enhance(np_img)
            return fromarray(np_img)
        if self.realcugan:
            return self.realcugan.process_pil(data.img)
