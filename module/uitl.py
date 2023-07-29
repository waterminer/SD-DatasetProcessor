from .data import Data
from .filter import Filter
from .processor import Processor,ProcessorError
import copy
import os

#文件分类
_img_ext=[".png",".jpg"] #支持的图片格式
_text_ext=[".txt"] #支持的标签格式

#匹配标签
def pair_token(token_list,data_list):
    for file_name in token_list:
        splitext = os.path.splitext(file_name)
        name = splitext[0]
        for data in data_list:
            if name == data.name:
                data.inputToken(file_name)

#读入文件的方法
def data_list_builder(input_dir)->list[Data]:
    data_list:list[Data]=[]
    token_list=[]
    for file_name in os.listdir(input_dir): #读取图片
        splitext = os.path.splitext(file_name)
        name = splitext[0]
        ext = splitext[1]
        #如果是图片
        if ext in _img_ext:
            img = Data(input_dir,name,ext)
            data_list.append(img)
        if ext in _text_ext:
            token_list.append(file_name)
        pair_token(token_list,data_list)
        token_list.clear()
    return data_list

def filter_manager(filters:Filter,data:Data)->bool:
    for filter in filters:
        fun = getattr(Filter,filter.get('filter'))
    if fun(data,filter.get('arg')):
        return True
    else:
        return False

def processor_manager(processors:dict,data:Data):
    newData=copy.deepcopy(data)
    for processor in processors:
        fun = getattr(Processor,processor.get('method'))
        try:
            if bool(processor.get("arg")):
                newData = fun(newData,processor.get("arg"))
            else:
                newData = fun(newData)
        except(ProcessorError):
            raise ProcessorError
    return newData