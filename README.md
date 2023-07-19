# 说明文档

## 使用方式

参考conf文件进行编写

```yaml
path:
  input: "" #输入路径
  output: "" #输出路径
conduct:
  - #处理组1 
    repeat: 3
    filter: [512,1536]
    processor:
    - #处理器1
      method: randomCrop
      arg: 512
  - #处理组2
    repeat: 3
    filter: [1536,2048]
    processor:
    - #处理器1
      method: resize
      arg: 0.75
    - #处理器2
      method: randomCrop
      arg: 512
  - #处理组3 
    processor:
    - #处理器1
      method: flip
```

## 处理器说明

|名称|说明|参数1|
| -- | -- | -- |
|randomCrop|随机裁切矩形图片|图片分辨率（整数）|
|flip|水平翻转图片| - |
|resize|按比例重新调整大小|比例（附点数）|
|force_resize|将图片缩放至特定大小|数组，输入格式为[x,y]|

## 控制器说明

与处理器不同，控制器负责流程控制，比如筛选特定尺寸的图片

|名称|说明|参数1|
| -- | -- | -- |
|filter|过虑特定尺寸的图片|数组，输入格式为[max,min]，缺省填-1 |
