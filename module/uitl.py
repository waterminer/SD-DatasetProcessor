from module import Data
from module import Filter
from module import Processor, ProcessorError
from .tools.tagger import Tagger,TaggerOption
from .tools.upscale import UpcaleOption,UpscaleModel
import copy
import os

# 文件分类
IMG_EXT = [".png", ".jpg"]  # 支持的图片格式
TEXT_EXT = [".txt"]  # 支持的标签格式

def tagger_bulider(args:dict)->Tagger:
    option = TaggerOption()
    if args.get('model_path'):
        option.model_path = args['model_path']
    if args.get('model_type'):
        option.model_type = args['model_type']
    if args.get('force_download'):
        option.force_download = args['force_download']
    if args.get('undesired_tags'):
        option.undesired_tags = args['undesired_tags']
    if args.get('batch_size'):
        option.batch_size = args['batch_size']
    if args.get('max_data_loader_n_workers'):
        option.max_data_loader_n_workers = args['max_data_loader_n_workers']
    if args.get('remove_underscore'):
        option.remove_underscore = args['remove_underscore']
    if args.get('thresh'):
        option.thresh = args['thresh']
    if args.get('character_threshold'):
        option.character_threshold = args['character_threshold']
    if args.get('general_threshold'):
        option.general_threshold = args['general_threshold']
    return Tagger(option)

def upscale_model_bulider(args:dict)->UpscaleModel:
    option = UpcaleOption
    if args.get('model_path'):
        UpcaleOption.model_path = args['model_path']
    if args.get('force_download'):
        UpcaleOption.force_download = args['force_download']
    if args.get('model_type'):
        UpcaleOption.model_type = args['model_type']
    if args.get('tile'):
        UpcaleOption.tile = args['tile']
    if args.get('tile_pad'):
        UpcaleOption.tile_pad = args['tile_pad']
    if args.get('pre_pad'):
        UpcaleOption.pre_pad = args['pre_pad']
    if args.get('half'):
        UpcaleOption.half = args['half']
    return UpscaleModel(option)

class MainOption:
    def __init__(self,args={}):
        if args.get('save_sorce_name'):
            self.save_sorce_name=args.get('save_sorce_name')
        else:self.save_sorce_name=False

        if args.get('save_conduct_id'):
            self.save_conduct_id=args.get('save_conduct_id')
        else:self.save_conduct_id=False

        if args.get('save_repeat'):
            self.save_repeat=args.get('save_repeat')
        else:self.save_repeat=False

        if args.get('save_sub'):
            self.save_sub=args.get('save_sub')
        else:self.save_sub=False

        if args.get('clean_tag'):
            self.clean_tag=args.get('clean_tag')
        else:self.clean_tag=False

        if args.get('tag_no_paired_data'):
            self.tag_no_paired_data=args.get('tag_no_paired_data')
        else:self.tag_no_paired_data=True

        if args.get('force_tag_all'):
            self.force_tag_all=args.get('force_tag_all')
        else:self.force_tag_all=False

class DatasetProcessor:
    def data_list_builder(self,input_dir:str)->list[Data]:...
    def pair_token(self,token_list: list, data_list: list[Data]):...
    def __init__(self,
                 input_dir:str,
                 output_dir:str,
                 conduct:dict,
                 option:dict|None=None,
                 tagger:dict|None=None,
                 upscale:dict|None=None
                 ):
        self.input_dir=input_dir
        self.conduct=conduct
        self.output_dir=output_dir
        if tagger:
            self.tagger = tagger_bulider(tagger)
        else: self.tagger = None
        if upscale:
            self.upscale = upscale_model_bulider(upscale)
        else: self.upscale = None
        if option:
            self.option = MainOption(option)
        else:
            self.option = MainOption()
        self.data_list = self.data_list_builder(input_dir)
        
    # 匹配标签
    def pair_token(self,token_file_list: list, data_list: list[Data]):
        no_paired_data_list = []
        for data in data_list:
            for file_name in token_file_list:
                splitext = os.path.splitext(file_name)
                name = splitext[0]
                if name == data.name:
                    data.input_token(file_name,self.option)
                    token_file_list.remove(file_name)
            if not data.token:
                no_paired_data_list.append(data)
        return no_paired_data_list

    # 读取文件并建立列表
    def data_list_builder(self,input_dir:str)->list[Data]:
        data_list: list[Data] = []
        token_list = []
        no_paired_data_list = []
        count = 0
        print("开始读取文件\n")
        for file_name in os.listdir(input_dir):  # 读取图片
            splitext = os.path.splitext(file_name)
            name = splitext[0]
            ext = splitext[1]
            # 如果是图片
            if ext in IMG_EXT:
                img = Data(input_dir, name, ext)
                data_list.append(img)
                count += 1
            if ext in TEXT_EXT:
                token_list.append(file_name)
            no_paired_data_list = self.pair_token(token_list, data_list)
        token_list.clear()
        print(
            "一共读取" + str(count) + "张图片,其中有" +
            str(no_paired_data_list.__len__()) + "张图片没有配对的标签"
        )
        if self.tagger:
            if self.option.tag_no_paired_data:
                print("已启用对未标签的图片进行打标")
                self.tagger.tag_data_list(no_paired_data_list)
            if self.option.force_tag_all:
                print("已强制对所有图片进行机器标注")
                self.tagger.tag_data_list(data_list)
        return data_list
    
    #过滤器管理
    def filter_manager(self,filter_list: list, data: Data) -> bool:
        flag=False
        for filter in filter_list:
            fun = getattr(Filter, filter.get('filter'))
            if filter.get('arg'):
                if fun(data, filter.get('arg')): return True
            else:
                if fun(data): return True
        return False

    #处理器管理
    def processor_manager(self,processor_list: list, data: Data):
        for processor in processor_list:
            try:
                fun = getattr(Processor, processor.get('method'))
                if fun == Processor.tag_image:
                    if self.tagger is None:
                        raise NoneTaggerError()
                    data = fun(data,self.tagger)
                if fun == Processor.upscale_image:
                    if self.upscale is None:
                        raise NoneUpscaleError()
                    data = fun(data,self.upscale)
                if bool(processor.get("arg")):
                    data = fun(data, processor.get("arg"))
                else:
                    data = fun(data)
            except ProcessorError:
                raise ProcessorError
            except AttributeError:
                print("输入错误：不存在的method："+processor.get('method')+"\n请检查配置文件")
                exit(1)
        return data


    def conduct_manager(self,conducts:list,data:Data)->Data:
        new_data = copy.deepcopy(data)
        for conduct in conducts:
            if conduct.get('sub_conduct'):
                sub_data = copy.copy(new_data)
                sub_data.conduct += "_sub["
                sub_data = self.conduct_manager(conduct.get('sub_conduct'),sub_data)
                if sub_data is not None:
                    sub_data.conduct += "]"
                    new_data.img = sub_data.img.copy()
                    new_data.conduct += sub_data.conduct
                    if self.option.save_sub:
                        sub_output=os.path.join(self.output_dir,"sub")
                        if not (os.path.exists(sub_output)):
                            os.mkdir(sub_output)
                        sub_data.save(sub_output,self.option)
            filters = conduct.get('filters')
            if filters:
                if self.filter_manager(filters, new_data): continue
            if bool(conduct.get('repeat')):
                repeat = conduct.get('repeat')
            else:
                repeat = 1
            for j in range(0, repeat):
                new_data.repeat = j
                try:
                    return self.processor_manager(conduct.get('processor'), new_data)
                except ProcessorError:
                    break

    def main(self):
        for i in range(0,len(self.data_list)):
            data = self.data_list.pop()
            data.id=i
            data = self.conduct_manager(self.conduct,data)
            if data is not None:
                data.save(self.output_dir,self.option)

class NoneTaggerError(RuntimeError):
    def __init__(self,name):
        print(f"Error:{name} is faild!")
        print("Tagger is not active!Please add this commit in config:")
        print("Tagger:\n\tactive: True")
class NoneUpscaleError(RuntimeError):
    def __init__(self,name):
        print(f"Error:{name} is faild!")
        print("Upscale is not active!Please add this commit in config:")
        print("upscale:\n\tactive: True")