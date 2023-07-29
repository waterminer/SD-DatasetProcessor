from huggingface_hub import hf_hub_download
from keras.models import load_model
import torch
from ..module.data import Data

from dataclasses import dataclass,field
import os
import enum

IMAGE_SIZE = 448

FILES = ["keras_metadata.pb", "saved_model.pb", "selected_tags.csv"]
SUB_DIR = "variables"
SUB_DIR_FILES = ["variables.data-00000-of-00001", "variables.index"]
CSV_FILE = FILES[-1]

class Repo_id(enum):
    WD14_MOAT="SmilingWolf/wd-v1-4-moat-tagger-v2"
    WD14_VIT="SmilingWolf/wd-v1-4-vit-tagger-v2"
    WD14_SWINV2="SmilingWolf/wd-v1-4-swinv2-tagger-v2"
    WD14_CONVNEXT="SmilingWolf/wd-v1-4-convnext-tagger-v2"
    WD14_CONVNEXT2="SmilingWolf/wd-v1-4-convnextv2-tagger-v2"

@dataclass
class TaggerOption:
    force_download:bool=field(default=False)
    model_path:str=field(default="./wd14")
    repo_id:Repo_id=field(default=Repo_id.WD14_CONVNEXT)

def tagger(datalist:list[Data],option:TaggerOption|None=TaggerOption()):
    print("开始自动打标")
    if not os.path.exists(option.modle_path) or option.force_download:
        print("Downloding model from huggingface:"+option.repo_id)
        os.mkdir(option.modle_path)
        for file in FILES:
            hf_hub_download(
                option.repo_id,
                filename=file,
                cache_dir=option.model_path,
                force_download=True,
                  force_filename=file)
        for file in SUB_DIR_FILES:
            hf_hub_download(
                option.repo_id,
                filename=file,
                subfolder=SUB_DIR,
                cache_dir=os.path.join(option.model_dir, SUB_DIR),
                force_download=True,
                force_filename=file,
            )
    print("Loading model...")
    moedl = load_model(option.model_path)
    for data in datalist:
        img = data.img
    