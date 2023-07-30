from .data import Data
class Filter:
    """
    此处用于编写过滤器
    """
    def img_filter(data:Data,size:list):
        max = size[1]
        min = size[0]
        if min != -1:
            if data.size[0] <= min or data.size[1] <= min:
                return True
        if max != -1:
            if data.size[0] > max or data.size[1] > max:
                return True
        else: return False
        
    def tag_filter(data:Data,tag):
        if tag in data.token: return True
        else: return False

    def tag_selecter(data:Data,tag):
        if tag in data.token: return False
        else: return True

    def tag_is_not_none(data:Data):
        if data.token: return False
        else: return True

    def tag_is_none(data:Data):
        if data.token: return True
        else: return False