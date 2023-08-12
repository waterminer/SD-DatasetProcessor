from dataset_processor import *

import yaml


if __name__ == "__main__":
    with open("./conf.yaml", "r", encoding="utf-8") as f:
        config = yaml.load(f.read(), yaml.FullLoader)
    # 设置
    input_dir = config.get('path').get('input')  # 输入目录
    output_dir = config.get('path').get('output')  # 输出目录
    # 参数
    conducts = config.get('conduct')
    option = config.get('option')
    tagger = config.get('tagger')
    upscale = config.get('upscale')
    DatasetProcessor(input_dir,output_dir,conducts,option,tagger,upscale).main()