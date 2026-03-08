# learning_logs/utils.py
from PIL import Image
import os
from django.conf import settings

def compress_image(image_path, max_size=(1920, 1080), quality=85):
    """
    压缩图片：
    - image_path: 图片的绝对路径
    - max_size: 最大尺寸（宽, 高），超过会等比例缩放
    - quality: 压缩质量（1-100），85兼顾画质和体积
    """
    try:
        # 打开图片
        img = Image.open(image_path)
        # 等比例缩放图片
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        # 保存压缩后的图片（覆盖原文件）
        img.save(
            image_path,
            optimize=True,  # 优化图片
            quality=quality,  # 压缩质量
            progressive=True  # 渐进式加载（网页显示更友好）
        )
        return True
    except Exception as e:
        print(f"图片压缩失败：{e}")
        return False