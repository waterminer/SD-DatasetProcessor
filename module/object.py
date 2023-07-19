from PIL import Image 
import os

class Data:
    token:list[str] = []
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
        self.token = file.read(-1).split(",")
        file.close
    
    #保存的方法
    def save(self,output_dir):
        savename=self.name+"_"+str(self.id)+self.conduct+str(self.repeat)
        self.img.save(os.path.join(output_dir,savename+self.ext))
        print(savename)
        file = open(os.path.join(output_dir,savename+".txt"),mode="x")
        file.write(self.token)
        file.close
        self.img.close

class Controler:
    def filter(data:Data,min,max):
        if min != -1:
            if data.size[0] <= min or data.size[1] <= min:
                return True
        if max != -1:
            if data.size[0] > max or data.size[1] > max:
                return True
        else:
            return False

