from module.processor import ProcessorError
from module.uitl import (
    data_list_builder,
    filter_manager,
    processor_manager
)
import os
import yaml

with open("./test.yaml","r",encoding="utf-8") as f:
    config=yaml.load(f.read(),yaml.FullLoader)
# 设置
input_dir = config.get('path').get('input') #输入目录
output_dir = config.get('path').get('output')  #输出目录
# 处理集
conducts = config.get('conduct')

def main(input_dir,output_dir,conducts):
    data_list=data_list_builder(input_dir)
    if not(os.path.exists(output_dir)):
        os.mkdir(output_dir)
    i = 0
    for i in range(0,len(data_list)):
        data = data_list.pop()
        for conduct in conducts:
            data.id=i
            filters = conduct.get('filters')
            if filters:
                if filter_manager(filters,data):continue
            if bool(conduct.get('repeat')):
                repeat=conduct.get('repeat')
            else: repeat = 1
            for j in range(0,repeat):
                data.repeat = j
                try:
                    processor_manager(conduct.get('processor'),data).save(output_dir)
                except ProcessorError:
                    break

if __name__ == "__main__":
    main(input_dir,output_dir,conducts)

# if not(os.path.exists(output_dir)):
#     os.mkdir(output_dir)
# i = 0
# for i in range(0,len(data_list)):
#     data = data_list.pop()
#     for conduct in conducts:
#         data.id=i
#         filters = conduct.get('filters')
#         flag=False
#         for filter in filters:
#             fun = getattr(Filter,filter.get('filter'))
#             if fun(data,filter.get('arg')):
#                 flag=True
#         if flag:
#             continue
#         if bool(conduct.get('repeat')):
#             repeat=conduct.get('repeat')
#         else: repeat = 1
#         for j in range(0,repeat):
#             try:
#                 data.repeat = j
#                 new = excute(data,conduct.get('processor'))
#                 new.save(output_dir)
#             except(processorError):
#                 break
