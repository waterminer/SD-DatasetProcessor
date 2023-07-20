# 说明文档

## 使用方式

参考conf文件进行编写

```yaml
path:
  input: "" #输入路径
  output: "" #输出路径

conduct:
  - #处理组1 此处示意为将所有大于512的图片进行翻转
    filters: #用于定义过滤器
    - #过滤器1
      filter: img_filter
      arg: [512,-1]
    processor: #用于定义处理器
    - #处理器1
      method: flip
      arg: 512

#以下为进阶示范
  - #处理组2 此处示意为将1024~2048区间大小的图片进行缩放然后进行随机裁切
    repeat: 3 #用于循环执行
    filters: #用于定义过滤器
    - #过滤器1
      filter: img_filter
      arg: [1024,2048]
    processor: #用于定义处理器
    - #处理器1
      method: resize
      arg: 0.5
    - #处理器2
      method: random_crop
      arg: 512
```

## 处理器说明

|名称|说明|参数|
| -- | -- | -- |
|random_crop|随机裁切矩形图片|图片分辨率（整数）|
|flip|水平翻转图片| - |
|resize|按比例重新调整大小|比例（附点数）|
|force_resize|将图片缩放至特定大小|数组，输入格式为[x,y]|
|append_tag|在标签组末尾加上标签|标签（文本）|
|remove_tag|删除标签组中符合条件的标签|标签（文本）|
|insert_tag|在标签组开头插入标签|标签（文本）|
|move_forward|将标签组末尾的标签移到开头|-|
|none|不做操作（用于特定场合）|-|

## 过滤器说明

负责过滤符合特定条件的数据

|名称|说明|参数|
| -- | -- | -- |
|img-filter|过虑特定尺寸的图片|数组，输入格式为[max,min]，缺省填-1 |
|tag_filter|过滤掉特定标签|标签（文本）|
|tag_selecter|须要包含特定标签|标签（文本）|
