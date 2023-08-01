from module import Data
from module import Filter
from module import Processor, ProcessorError
from .tools.tagger import Tagger
import copy
import os

# 文件分类
IMG_EXT = [".png", ".jpg"]  # 支持的图片格式
TEXT_EXT = [".txt"]  # 支持的标签格式


# 匹配标签
def pair_token(token_list: list, data_list: list):
    no_paired_data_list = []
    for data in data_list:
        for file_name in token_list:
            splitext = os.path.splitext(file_name)
            name = splitext[0]
            if name == data.name:
                data.input_token(file_name)
                token_list.remove(file_name)
        if not data.token:
            no_paired_data_list.append(data)
    return no_paired_data_list


# 读入文件的方法
def data_list_builder(input_dir,tagger:Tagger|None=None) -> list[Data]:
    data_list: list[Data] = []
    token_list = []
    no_paired_data_list = []
    count = 0
    for file_name in os.listdir(input_dir):  # 读取图片
        splitext = os.path.splitext(file_name)
        name = splitext[0]
        ext = splitext[1]
        # 如果是图片
        if ext in IMG_EXT:
            img = Data(input_dir, name, ext)
            data_list.append(img)
            count += 1
        if ext in TEXT_EXT:
            token_list.append(file_name)
        no_paired_data_list = pair_token(token_list, data_list)
    token_list.clear()
    print(
        "一共读取" + str(count) + "张图片,其中有" +
        str(no_paired_data_list.__len__()) + "张图片没有配对的标签"
    )
    if tagger:
        print("已启用打标")
        tagger.tag_data_list(no_paired_data_list)
    return data_list


def filter_manager(filter_list: list, data: Data) -> bool:
    for filter in filter_list:
        fun = getattr(Filter, filter.get('filter'))
        if fun(data, filter.get('arg')):
            return True
        else:
            return False


def processor_manager(processor_list: list, data: Data):
    new_data = copy.deepcopy(data)
    for processor in processor_list:
        fun = getattr(Processor, processor.get('method'))
        try:
            if bool(processor.get("arg")):
                new_data = fun(new_data, processor.get("arg"))
            else:
                new_data = fun(new_data)
        except ProcessorError:
            raise ProcessorError
    return new_data
