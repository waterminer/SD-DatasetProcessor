from random import randint as random
from .data import Data
from PIL import Image 
from PIL import ImageEnhance
import copy

class Processor(Data):
    #在这里定义处理方法
    '''
    编写规范如下:
    def 处理名(data:Data,args):
        #代码块
        return data
    '''
    def random_crop(data,size):
        if not(data.size[0] <= size or data.size[1] <= size):
            x = random(1,data.size[0]-size)
            y = random(1,data.size[1]-size)
            box = (x,y,x+size,y+size)
            data.img = data.img.crop(box)
            data.conduct+="_rc"
            data.size = data.img.size
        else:
            print(data.name+data.ext+"图片过小，已跳过")
            raise processorError
        return data
    
    def flip(data):
        data.img = data.img.transpose(Image.FLIP_LEFT_RIGHT)
        data.conduct+="_f"
        return data

    def resize(data:Data,proportion:float):
        data.size=(int(data.size[0]*proportion),int(data.size[1]*proportion))
        data.img = data.img.resize(data.size)
        data.conduct+="_r"
        return data

    def force_resize(data:Data,size:list):
        data.size=(size[0],size[1])
        data.img=data.img.resize(data.size)
        data.conduct+="_fr"
        return data

    def none(data:Data):
        """
        无操作，主要用于一些特殊场景
        """
        return data
    
    def append_tag(data:Data,tag:str):
        Data.token.append(tag)
        return data
    
    def remove_tag(data:Data,tag:str):
        Data.token.remove(tag)
        return data
    
    def insert_tag(data:Data,tag:str):
        Data.token.insert(0,tag)
        return data
    
    def move_forward(data:Data):
        """
        将Tag里最后一位放到开头
        """
        token=data.token.pop()
        Data.token.insert(0,token)
        return data
    
#一个自定义的异常
class processorError(RuntimeError):
    pass

# 执行处理的方法
def excute(data:Data,conducts:dict):
    newData=copy.deepcopy(data)
    for conduct in conducts:
        processor = getattr(Processor,conduct.get('method'))
        try:
            if bool(conduct.get("arg")):
                newData = processor(newData,conduct.get("arg"))
            else:
                newData = processor(newData)
        except(processorError):
            raise processorError
    return newData