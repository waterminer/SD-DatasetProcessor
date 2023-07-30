from huggingface_hub import hf_hub_download
from keras.models import load_model
import numpy as np
import cv2
import torch

from module import Data

from dataclasses import dataclass, field
import os
from enum import Enum
import csv

IMAGE_SIZE = 448

FILES = ["keras_metadata.pb", "saved_model.pb", "selected_tags.csv"]
SUB_DIR = "variables"
SUB_DIR_FILES = ["variables.data-00000-of-00001", "variables.index"]
CSV_FILE = FILES[-1]
MODEL_AUTHOR_ID = "SmilingWolf/"


class ModelType(Enum):
    WD14_MOAT = "wd-v1-4-moat-tagger-v2"
    WD14_VIT = "wd-v1-4-vit-tagger-v2"
    WD14_SWINV2 = "wd-v1-4-swinv2-tagger-v2"
    WD14_CONVNEXT = "wd-v1-4-convnext-tagger-v2"
    WD14_CONVNEXT2 = "wd-v1-4-convnextv2-tagger-v2"


@dataclass
class TaggerOption:
    force_download: bool = field(default=False)
    model_type: ModelType = field(default=ModelType.WD14_CONVNEXT)
    model_path: str = field(default="./models")


def preprocess_image(image):
    image = np.array(image)
    image = image[:, :, ::-1]  # RGB->BGR

    # pad to square
    size = max(image.shape[0:2])
    pad_x = size - image.shape[1]
    pad_y = size - image.shape[0]
    pad_l = pad_x // 2
    pad_t = pad_y // 2
    image = np.pad(image,
                   ((pad_t, pad_y - pad_t),
                    (pad_l, pad_x - pad_l), (0, 0)),
                   mode="constant",
                   constant_values=255)

    interp = cv2.INTER_AREA if size > IMAGE_SIZE else cv2.INTER_LANCZOS4
    image = cv2.resize(image, (IMAGE_SIZE, IMAGE_SIZE), interpolation=interp)

    image = image.astype(np.float32)
    return image


class ImageLoadingPrepDataset(torch.utils.data.Dataset):
    def __init__(self, images):
        self.images = images

    def __getitem__(self,idx):
        image = preprocess_image(self.images[idx])
        tensor = torch.tensor(image)
        return tensor, image


def tagger(datalist: list[Data], option: TaggerOption | None = TaggerOption()):
    print("开始自动打标")
    repo_id = MODEL_AUTHOR_ID + option.model_type.value
    model_path = os.path.join(option.model_path, option.model_type.value)
    if not os.path.exists(model_path) or option.force_download:
        print("Downloading model from huggingface:" + repo_id)
        os.mkdir(option.model_path)
        for file in FILES:
            hf_hub_download(
                repo_id,
                filename=file,
                cache_dir=model_path,
                force_download=True,
                force_filename=file)
        for file in SUB_DIR_FILES:
            hf_hub_download(
                repo_id,
                filename=file,
                subfolder=SUB_DIR,
                cache_dir=os.path.join(model_path, SUB_DIR),
                force_download=True,
                force_filename=file,
            )
    print("Loading model...")
    model = load_model(model_path)
    with open(os.path.join(model_path, CSV_FILE), "r", -1, "utf-8") as f:
        reader = csv.reader(f)
        line = [row for row in reader]
        header = line[0]
        rows = line[1:]
    assert header[0] == "tag_id" and header[1] == "name" and header[2] == "category", f"unexpected csv format: {header}"
    general_tags = [row[1] for row in rows[1:] if row[2] == "0"]
    character_tags = [row[1] for row in rows[1:] if row[2] == "4"]

    img_list = [data.img for data in datalist]
    tag_freq = {}
    ImageLoadingPrepDataset(img_list)