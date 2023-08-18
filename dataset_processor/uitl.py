from tqdm import tqdm

from dataset_processor import Data
from dataset_processor import Filter
from dataset_processor import Processor, ProcessorError
from .tools.tagger import Tagger, TaggerOption, ModelType as TaggerType
from .tools.upscale import UpcaleOption, UpscaleModel, ModelType as UpscaleType
import copy
import os

# 文件分类
IMG_EXT = [".png", ".jpg"]  # 支持的图片格式
TEXT_EXT = [".txt"]  # 支持的标签格式


def tagger_builder(args: dict) -> Tagger:
    option = TaggerOption()
    if args.get('model_path'):
        option.model_path = args['model_path']
    if args.get('model_type'):
        try:
            option.model_type = TaggerType[args['model_type']]
        except KeyError:
            print(f"Invalid type:{args['model_type']}")
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


def upscale_model_builder(args: dict) -> UpscaleModel:
    option = UpcaleOption()
    if args.get('model_path'):
        UpcaleOption.model_path = args['model_path']
    if args.get('force_download'):
        UpcaleOption.force_download = args['force_download']
    if args.get('model_type'):
        try:
            UpcaleOption.model_type = UpscaleType[args['model_type']]
        except KeyError:
            print(f"Invalid type:{args['model_type']}")
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
    def __init__(self, args={}):
        if args.get('save_source_name'):
            self.save_source_name = args.get('save_source_name')
        else:
            self.save_source_name = False

        if args.get('save_conduct_id'):
            self.save_conduct_id = args.get('save_conduct_id')
        else:
            self.save_conduct_id = False

        if args.get('save_sub'):
            self.save_sub = args.get('save_sub')
        else:
            self.save_sub = False

        if args.get('clean_tag'):
            self.clean_tag = args.get('clean_tag')
        else:
            self.clean_tag = True

        if args.get('tag_no_paired_data'):
            self.tag_no_paired_data = args.get('tag_no_paired_data')
        else:
            self.tag_no_paired_data = True

        if args.get('force_tag_all'):
            self.force_tag_all = args.get('force_tag_all')
        else:
            self.force_tag_all = False

        if args.get('custom_name'):
            self.custom_name = args.get('custom_name')
        else:
            self.custom_name = None

class DatasetProcessor:
    """
    构建DatasetProcessor对象以开始数据处理
    """
    upscale: UpscaleModel = None
    tagger: Tagger = None
    option: MainOption = None

    def data_list_builder(self, input_dir: str) -> list[Data]:
        ...

    def pair_token(self, token_file_list: list, data_list: list[Data]):
        ...

    def __init__(self,
                 input_dir: str,
                 output_dir: str,
                 conduct: dict,
                 option: dict | None = None,
                 tagger: dict | None = None,
                 upscale: dict | None = None
                 ):
        self.input_dir = input_dir
        self.conduct = conduct
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.output_dir = output_dir
        if tagger and tagger.get('active'): self.tagger = tagger_builder(tagger)
        if upscale and upscale.get('active'): self.upscale = upscale_model_builder(upscale)
        if option:
            self.option = MainOption(option)
        else:
            self.option = MainOption()
        self.data_list = self.data_list_builder(input_dir)

    # 匹配标签
    def pair_token(self, token_file_list: list, data_list: list[Data]):
        no_paired_data_list = []
        for data in data_list:
            for file_name in token_file_list:
                splitext = os.path.splitext(file_name)
                name = splitext[0]
                if name == data.name:
                    data.input_token(file_name, self.option)
                    token_file_list.remove(file_name)
            if not data.token:
                no_paired_data_list.append(data)
        return no_paired_data_list

    # 读取文件并建立列表
    def data_list_builder(self, input_dir: str) -> list[Data]:
        data_list: list[Data] = []
        token_list = []
        no_paired_data_list = []
        count = 0
        print("load files...\n开始读取文件...")
        for file_name in tqdm(os.listdir(input_dir)):
            splitext = os.path.splitext(file_name)
            name = splitext[0]
            ext = splitext[1]
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
            if self.option.tag_no_paired_data and no_paired_data_list != []:
                print("已启用对未标签的图片进行打标")
                self.tagger.tag_data_list(no_paired_data_list)
            if self.option.force_tag_all:
                print("已强制对所有图片进行机器标注")
                self.tagger.tag_data_list(data_list)
        return data_list

    # 过滤器管理
    def filter_manager(self, filter_list: list, data: Data) -> bool:
        flag = False
        for filter in filter_list:
            fun = getattr(Filter, filter.get('filter'))
            if filter.get('arg'):
                return fun(data, filter.get('arg'))
            else:
                return fun(data)
        return False

    # 处理器管理
    def processor_manager(self, processor_list: list, data: Data):
        for processor in processor_list:
            try:
                fun = getattr(Processor, processor.get('method'))
                if fun == Processor.tag_image:
                    if self.tagger is None:
                        raise NoneTaggerError('tag_image')
                    data = fun(data, self.tagger)
                elif fun == Processor.upscale_image:
                    if self.upscale is None:
                        raise NoneUpscaleError('upscale_image')
                    data = fun(data, self.upscale)
                elif bool(processor.get("arg")):
                    data = fun(data, processor.get("arg"))
                else:
                    data = fun(data)
            except ProcessorError:
                raise ProcessorError
            except AttributeError:
                print(f"\nError:Invalid method: {processor.get('method')}\nPlease check the config file")
                exit(1)
            except NoneUpscaleError as e:
                print(f"\nError:{e.name} is faild!")
                print("Upscale is not active!Please add this commit in config:")
                print("======================")
                print("upscale:\n  active: True")
                print("======================")
                exit(1)
            except NoneTaggerError as e:
                print(f"\nError:{e.name} is faild!")
                print("Tagger is not active!Please add this commit in config:")
                print("======================")
                print("Tagger:\n  active: True")
                print("======================")
                exit(1)
        return data

    def conduct_manager(self, conducts: list[dict], data_list: list[Data],output_dir:str) -> list[tuple[Data,str]]:
        """
        处理行为管理函数，虽然可以接受data_list，但是存在文件名碰撞隐患
        推荐只传入一个data对象
        返回一个元素为(data,save_path)的列表，save_path是data的对应保存地址
        """
        return_list = []
        for conduct in conducts:
            save_path = output_dir #初始化保存地址
            if conduct.get('sub_conduct'):
                sub_data_list = [copy.copy(data) for data in data_list]
                for data in sub_data_list:
                    data.conduct += "_sub["
                #请原谅我写成这么样的一坨，我也想不到有什么好办法
                if self.option.save_sub:
                    sub_output = os.path.join(output_dir, "sub")
                    if not (os.path.exists(sub_output)):
                        os.mkdir(sub_output)
                sub_data_list = self.conduct_manager(conduct.get('sub_conduct'), sub_data_list,sub_output)
                if sub_data_list:
                    data_list = []
                    for data,_ in sub_data_list:
                        data.conduct += "]"
                        data_list.append(copy.deepcopy(data))
                    if self.option.save_sub:
                        for sub_data,sub_save_path in sub_data_list:
                            sub_data.save(sub_save_path, self.option)
            for data in data_list:
                filters = conduct.get('filters')
                if filters:
                    if self.filter_manager(filters, data): continue
                if bool(conduct.get('repeat')):
                    repeat = conduct.get('repeat')
                else:
                    repeat = 1
                if conduct.get('custom_sub_folder'):
                    if conduct.get('custom_sub_folder') == "sub":
                        print("Invalid folder name Error:custom_sub_folder can not be \"sub\"!")
                        raise(InvalidFolderNameRrror)
                    save_path=os.path.join(output_dir,conduct.get('custom_sub_file'))
                    if not (os.path.exists(save_path)):
                        os.mkdir(save_path)
                for j in range(0, repeat):
                    data.repeat = j
                    try:
                        return_list.append(
                            (self.processor_manager(conduct.get('processor'), copy.deepcopy(data)),save_path)
                            )
                    except ProcessorError:
                        break
        return return_list

    def main(self):
        """
        主入口
        """
        print("开始图片处理...")
        for i in tqdm(range(0, len(self.data_list))):
            data = self.data_list.pop()
            data.id = i
            data_list = self.conduct_manager(self.conduct, [data], self.output_dir)
            if data_list:
                for data,save_path in data_list:
                    data.save(save_path, self.option)


class NoneTaggerError(RuntimeError):
    def __init__(self, name):
        self.name = name


class NoneUpscaleError(RuntimeError):
    def __init__(self, name):
        self.name = name

class InvalidFolderNameRrror(RuntimeError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)