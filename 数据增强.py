from random import randint as random
from PIL import Image 
from PIL import ImageEnhance
import os

# 设置
input_dir = "E:\\LoRa\\dataset\\coppermix-dataset\\1_shiratama" #输入目录
output_dir = "G:\\modes\\datasets\\1_out" #输出目录
repeat = 4 #重复次数
method = ["randomcorp"] #处理方法

#数据对象定义
class Data:
    method = ""
    # 图片读取并初始化
    def __init__(self,path:str,name:str,ext:str):
        self.name = name
        self.ext = ext
        self.path = path
        #读取图片
        self.img = Image.open(os.path.join(path,name+ext))
        self.size = self.img.size
    # 随机裁切方法
    def randomCorp(self,size):
        token = True
        if not(self.size[0] <= size or self.size[1] <= size):
            x = random(1,self.size-size)
            y = random(1,self.size-size)
            box = (x,y,x+size,y+size)
            self.img.corp(box)
            self.method+="_rc"
            self.size = self.img.size
        else:
            print("图片过大，已跳过")
            token = False
        return token
    #保存的方法
    def save(self,output_dir):
        self.img.save(os.path.join(output_dir,self.name+self.method+self.ext))

    def inputToken(self,filename:str):
        file = open(os.path.join(input_dir,file_name),"r")
        self.token = file.read()
        file.close

#文件分类
img_ext=[".png",".jpg"] #支持的图片格式
text_ext=[".txt"] #支持的标签格式

#开始读入文件
data_list=[]
token_list=[]
if not(os.path.exists(output_dir)):
    os.mkdir(output_dir)
for file_name in os.listdir(input_dir): #读取图片
    splitext = os.path.splitext(file_name)
    name = splitext[0]
    ext = splitext[1]
    #如果是图片
    if ext in img_ext:
        img = Data(input_dir,name,ext)
        data_list.append(img)
    if ext in text_ext:
        token_list.append(file_name)

#匹配标签
for file_name in token_list:
    splitext = os.path.splitext(file_name)
    name = splitext[0]
    for data in data_list:
        if name == data.name:
            data.inputToken(file_name)