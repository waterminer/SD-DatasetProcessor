from src.utils import excute
from src.utils import Data
import os

# 设置
input_dir = "" #输入目录
output_dir = "" #输出目录
repeat = 4 #重复次数
#处理方法
img_conducts = [[{'method':"randomcrop",'args':512}],[{'method':"randomcrop",'args':512},{'method':"flip"}],[{'method':"flip"}]]

#文件分类
img_ext=[".png",".jpg"] #支持的图片格式
text_ext=[".txt"] #支持的标签格式

#开始读入文件
data_list:list[Data]=[]
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

new_list=data_list.copy()
i = 0
for data in data_list:
    for img_conduct in img_conducts:
        data.id=i
        new_list.append(excute(data,img_conduct))
    i += 1

for data in new_list:
    data.save(output_dir)