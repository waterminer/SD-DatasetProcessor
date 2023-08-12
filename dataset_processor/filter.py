from .data import Data


class Filter:
    """
    这是一个过滤器类，包含所有有关数据过滤的函数
    编写规范如下：
    def 过滤器名(data:Data,arg)->bool:
        #代码块
        return bool
    其中，True表示该数据会被过滤，False则会被保留
    """

    def img_size(data: Data, size: list) -> bool:
        min, max = tuple(size)
        x, y = data.size
        if min != -1:
            if data.size[0] <= min or data.size[1] <= min:
                return True
        if max != -1:
            if data.size[0] > max and data.size[1] > max:
                return True
        else:
            return False

    def tag_filter(data: Data, tag) -> bool:
        if tag in data.token:
            return True
        else:
            return False

    def tag_selector(data: Data, tag) -> bool:
        if tag in data.token:
            return False
        else:
            return True

    def tag_is_not_none(data: Data) -> bool:
        if data.token:
            return False
        else:
            return True

    def tag_is_none(data: Data) -> bool:
        if data.token:
            return True
        else:
            return False
