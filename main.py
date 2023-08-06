from module import ProcessorError
from module.uitl import *

from module.tools.tagger import Tagger

import os
import yaml


def main(input_dir, output_dir, conducts,option:dict|None=None, tagger:Tagger|None=None):
    data_list = data_list_builder(input_dir,tagger)
    if not (os.path.exists(output_dir)):
        os.mkdir(output_dir)
    i = 0
    for i in range(0, len(data_list)):
        data = data_list.pop()
        data.id = i
        data = conduct_manager(conducts,data,output_dir,option)
        if data is None:
            continue
        else:
            data.save(output_dir,option)


if __name__ == "__main__":
    with open("./test.yaml", "r", encoding="utf-8") as f:
        config = yaml.load(f.read(), yaml.FullLoader)
    # 设置
    input_dir = config.get('path').get('input')  # 输入目录
    output_dir = config.get('path').get('output')  # 输出目录
    # 参数
    conducts = config.get('conduct')
    option = config.get('option')
    tagger = config.get('tagger')

    if tagger:
        if tagger['active']:
           tagger=tagger_bulider(tagger)
        else: tagger=None
    main(input_dir,output_dir,conducts,option,tagger=tagger)