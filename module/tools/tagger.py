from huggingface_hub import hf_hub_download
from keras.models import load_model
import torch
from tqdm import tqdm
import numpy as np
import cv2


from module import Data
from dataclasses import dataclass, field
import os
from enum import Enum
import csv

IMAGE_SIZE = 448

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
    undesired_tags: str = field(default="")
    batch_size:int = field(default=1)
    max_data_loader_n_workers: int = field(default=None)
    remove_underscore:bool = field(default=True)
    thresh:float = field(default=0.35)
    character_threshold:float = field(default=None)
    general_threshold:float = field(default=None)
    

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

def collate_fn_remove_corrupted(batch):
    """Collate function that allows to remove corrupted examples in the
    dataloader. It expects that the dataloader returns 'None' when that occurs.
    The 'None's in the batch are removed.
    """
    # Filter out all the Nones (corrupted examples)
    batch = list(filter(lambda x: x is not None, batch))
    return batch

class ImageLoadingPrepDataset(torch.utils.data.Dataset):
    def __init__(self,data_list:list[Data]) -> None:
        self.dataset = []
        for data in data_list:
            self.dataset.append(
                {'img':data.img,
                 'sorce_data':data
                }
                )
    def __len__(self):
        return len(self.dataset)
    
    def __getitem__(self,idx):
        sorce_data = self.dataset[idx]['sorce_data']
        img = self.dataset[idx]['img']
        img= preprocess_image(img)
        tensor = torch.tensor(img)
        return (tensor, sorce_data)

class Tagger:

    FILES = ["keras_metadata.pb", "saved_model.pb", "selected_tags.csv"]
    SUB_DIR = "variables"
    SUB_DIR_FILES = ["variables.data-00000-of-00001", "variables.index"]
    CSV_FILE = FILES[-1]
    MODEL_AUTHOR_ID = "SmilingWolf/"


    def __init__ (self,option: TaggerOption | None = TaggerOption()):
        print("Init tagger...")
        self.repo_id = self.MODEL_AUTHOR_ID + option.model_type.value
        self.model_path = os.path.join(option.model_path, option.model_type.value)
        if not os.path.exists(self.model_path) or option.force_download:
            print("Downloading model from huggingface:" + self.repo_id)
            os.mkdir(self.model_path)
            for file in self.FILES:
                hf_hub_download(
                    self.repo_id,
                    filename=file,
                    cache_dir=self.model_path,
                    force_download=True,
                    force_filename=file)
            for file in self.SUB_DIR_FILES:
                hf_hub_download(
                    self.repo_id,
                    filename=file,
                    subfolder=self.SUB_DIR,
                    cache_dir=os.path.join(self.model_path, self.SUB_DIR),
                    force_download=True,
                    force_filename=file,
                )
        print("Loading model...")
        self.model = load_model(self.model_path)
        with open(os.path.join(self.model_path, self.CSV_FILE), "r", -1, "utf-8") as f:
            reader = csv.reader(f)
            line = [row for row in reader]
            header = line[0]
            rows = line[1:]
        assert header[0] == "tag_id" and header[1] == "name" and header[2] == "category", f"unexpected csv format: {header}"
        self.general_tags = [row[1] for row in rows[1:] if row[2] == "0"]
        self.character_tags = [row[1] for row in rows[1:] if row[2] == "4"]
        self.tag_freq = {}
        self.undesired_tags = set(option.undesired_tags.split(","))
        self.batch_size = option.batch_size
        self.max_data_loader_n_workers = option.max_data_loader_n_workers
        self.remove_underscore = option.remove_underscore
        self.thresh = option.thresh
        if option.character_threshold is None:
            self.character_threshold = self.thresh
        else:
            self.character_threshold = option.character_threshold
        if option.general_threshold is None:
            self.general_threshold = self.thresh
        else:
            self.general_threshold = option.general_threshold
        self.debug = False


    def run_batch(self,batchs):
        imgs = np.array([im for _, im in batchs])

        probs = self.model(imgs, training=False)
        probs = probs.numpy()

        for (sorce_data, _), prob in zip(batchs, probs):
            # 最初の4つはratingなので無視する
            # # First 4 labels are actually ratings: pick one with argmax
            # ratings_names = label_names[:4]
            # rating_index = ratings_names["probs"].argmax()
            # found_rating = ratings_names[rating_index: rating_index + 1][["name", "probs"]]

            # それ以降はタグなのでconfidenceがthresholdより高いものを追加する
            # Everything else is tags: pick any where prediction confidence > threshold
            combined_tags = []
            general_tag_text = ""
            character_tag_text = ""
            for i, p in enumerate(prob[4:]):
                if i < len(self.general_tags) and p >= self.general_threshold:
                    tag_name = self.general_tags[i]
                    if self.remove_underscore and len(tag_name) > 3:  # ignore emoji tags like >_< and ^_^
                        tag_name = tag_name.replace("_", " ")

                    if tag_name not in self.undesired_tags:
                        self.tag_freq[tag_name] = self.tag_freq.get(tag_name, 0) + 1
                        general_tag_text += ", " + tag_name
                        combined_tags.append(tag_name)
                elif i >= len(self.general_tags) and p >= self.character_threshold:
                    tag_name = self.character_tags[i - len(self.general_tags)]
                    if self.remove_underscore and len(tag_name) > 3:
                        tag_name = tag_name.replace("_", " ")

                    if tag_name not in self.undesired_tags:
                        self.tag_freq[tag_name] = self.tag_freq.get(tag_name, 0) + 1
                        character_tag_text += ", " + tag_name
                        combined_tags.append(tag_name)

                # 先頭のカンマを取る
            if len(general_tag_text) > 0:
                general_tag_text = general_tag_text[2:]
            if len(character_tag_text) > 0:
                character_tag_text = character_tag_text[2:]
            tag_text = ", ".join(combined_tags)
            sorce_data.token = combined_tags
            if self.debug:
                print("Character tags: "+
                      character_tag_text+
                      "\n  General tags: "+
                      general_tag_text)


    def tag_data_list(self,data_list:list[Data]):
        dataset = ImageLoadingPrepDataset(data_list)
        if self.max_data_loader_n_workers is not None:
            tensor_data = torch.utils.data.DataLoader(
                dataset,
                batch_size=self.batch_size,
                shuffle=False,
                num_workers=self.max_data_loader_n_workers,
                collate_fn=collate_fn_remove_corrupted,
                drop_last=False
            )
        else:
            tensor_data = [[(None,data)] for data in data_list]
        b_imgs = []
        for data_entry in tqdm(tensor_data,smoothing=0.0):
            for tensor_data in data_entry:
                if tensor_data is None:
                    continue
                image, sorce_data = tensor_data
                for data in data_list:
                    if sorce_data.name == data.name:
                        sorce_data = data
                if image is not None:
                    image = image.detach().numpy()
                else:
                    image = sorce_data.img
                    if image.mode != "RGB":
                        image = image.convert("RGB")
                    image = preprocess_image(image)
                b_imgs.append((sorce_data, image))
                if len(b_imgs) >= self.batch_size:
                    b_imgs = [(sorce_data, image) for sorce_data, image in b_imgs]  # Convert image_path to string
                    self.run_batch(b_imgs)
                    b_imgs.clear()

        if len(b_imgs) > 0:
            b_imgs = [(sorce_data, image) for sorce_data, image in b_imgs]  # Convert image_path to string
            self.run_batch(b_imgs)

    def tag_data(self,data:Data):
        img = preprocess_image(data.img)
        b_imgs = [(data,img)]
        self.run_batch(b_imgs)
        return data
        
