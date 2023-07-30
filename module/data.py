from PIL import Image
import os


class Data:

    # 图片读取并初始化
    def __init__(self, path: str, name: str, ext: str):
        self.token: list[str] = []
        self.conduct = ""
        self.repeat = 0
        self.id = 0
        self.name = name
        self.ext = ext
        self.path = path
        # 读取图片
        self.img = Image.open(os.path.join(path, name + ext))
        self.size = self.img.size

    # 载入标签
    def input_token(self, file_name: str):
        with open(os.path.join(self.path, file_name), "r") as f:
            self.token = f.read(-1).split(",")

    # 保存的方法
    def save(self, output_dir):
        save_name = self.name + "_" + str(self.id) + self.conduct + str(self.repeat)
        self.img.save(os.path.join(output_dir, save_name + self.ext))
        print(save_name)
        with open(os.path.join(output_dir, save_name + ".txt"), mode="w") as f:
            text = ",".join(self.token)
            f.write(text)
        self.img.close()
