from dataset_processor import *

import yaml
from argparse import ArgumentParser

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        '--input_dir',
        default=None,
        type=str,
        help='input dir,if used,it will cover config ''input_dir''//数据集输入路径,如果指定则会覆盖配置文件中的''input_dir'''
    )
    parser.add_argument(
        '--output_dir',
        default=None,
        type=str,
        help='output dir,if used,it will cover config ''output_dir''//数据集输入路径,如果指定则会覆盖配置文件中的''output_dir'''
    )
    parser.add_argument(
        '--config',
        default='./conf.yaml',
        type=str,
        help='yaml config path,default to reading conf.yaml in the root directory//指定yaml配置文件,默认读取根目录下conf.yaml'
    )
    args = parser.parse_args()
    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.load(f.read(), yaml.FullLoader)
    # 设置
    if args.input_dir:
        input_dir = args.input_dir
    else:
        input_dir = config.get('path').get('input')  # 输入目录
    if args.input_dir:
        output_dir = args.output_dir
    else:
        output_dir = config.get('path').get('output')  # 输出目录
    # 参数
    conducts = config.get('conduct')
    option = config.get('option')
    tagger = config.get('tagger')
    upscale = config.get('upscale')
    DatasetProcessor(input_dir,output_dir,conducts,option,tagger,upscale).main()