from random import randint as random
from PIL import Image 
from PIL import ImageEnhance
import copy
import os

class Data:
    conduct = ""
    repeat = 0
    id = 0
    # 图片读取并初始化
    def __init__(self,path:str,name:str,ext:str):
        self.name = name
        self.ext = ext
        self.path = path
        #读取图片
        self.img = Image.open(os.path.join(path,name+ext))
        self.size = self.img.size

    # 载入标签
    def inputToken(self,file_name:str):
        file = open(os.path.join(self.path,file_name),"r")
        self.token = file.read(-1)
        file.close
    
    #保存的方法
    def save(self,output_dir):
        savename=self.name+"_"+str(self.id)+self.conduct
        self.img.save(os.path.join(output_dir,savename+self.ext))
        file = open(os.path.join(output_dir,savename+".txt"),mode="x")
        print(savename)
        file.write(self.token)
        file.close
        self.img.close

# 执行处理的方法
def excute(data,conducts:dict):
    newData=copy.copy(data)
    for conduct in conducts:
        if conduct['method']== "randomcrop":
            Conduct.randomCrop(newData,conduct['args'])
        if conduct['method'] == "flip":
            Conduct.flip(newData)
    return newData

class Conduct(Data):

    def randomCrop(self,size):
        if not(self.size[0] <= size or self.size[1] <= size):
            token=True
            x = random(1,self.size[0]-size)
            y = random(1,self.size[1]-size)
            box = (x,y,x+size,y+size)
            self.img = self.img.crop(box)
            self.conduct+="_rc"
            self.size = self.img.size
        else:
            print("图片过大，已跳过")
            token = False
        return token
    
    def flip(self):
        token=True
        self.img = self.img.transpose(Image.FLIP_LEFT_RIGHT)
        self.conduct+="_f"
        return token