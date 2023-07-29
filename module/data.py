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
        with open(os.path.join(self.path,file_name),"r") as f:
            self.token = f.read(-1).split(",")
    
    #保存的方法
    def save(self,output_dir):
        savename=self.name+"_"+str(self.id)+self.conduct+str(self.repeat)
        self.img.save(os.path.join(output_dir,savename+self.ext))
        print(savename)
        with open(os.path.join(output_dir,savename+".txt"),mode="w") as f:
            text=",".join(self.token)
            f.write(text)
        self.img.close
