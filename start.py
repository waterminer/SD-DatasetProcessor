from module.object import Data
from module.object import Controler
from module.processor import excute
from module.processor import processorError
import os
import yaml

with open("./conf.yaml","r",encoding="utf-8") as f:
    config=yaml.load(f.read(),yaml.FullLoader)
# 设置
input_dir = config.get('path').get('input') #输入目录
output_dir = config.get('path').get('output')  #输出目录
#处理方法
conducts = config.get('conduct')

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
token_list.clear()

#执行处理
i = 0
for i in range(0,len(data_list)):
    data = data_list.pop()
    for conduct in conducts:
        data.id=i
        if bool(conduct.get('filter')):
            if Controler.filter(data,conduct.get('filter')[0],conduct.get('filter')[1]):
                continue
        if bool(conduct.get('repeat')):
            repeat=conduct.get('repeat')
        else: repeat = 1
        for j in range(0,repeat):
            try:
                data.repeat = j
                new = excute(data,conduct.get('processor'))
                new.save(output_dir)
            except(processorError):
                break
# for data in data_list:
#     for conduct in conducts:
#         data.id=i
#         if bool(conduct.get('repeat')):
#             data.repeat=conduct.get('repeat')
#         for j in range(0,data.repeat):
#             try:
#                 excute(data,conduct.get('processor')).save(output_dir)
#             except:
#                 break