# -*- coding: utf-8 -*-
"""
咪噜眼睛改色脚本
- 只在头部区域（head bbox: x 2~272, y 2~160，基于 339x336 原图坐标系）找深色眼球块
- 连通域面积 >= 300 才认为是眼球，避免误伤描边细线
- 想改成别的颜色：改下面 EYE_COLOR 的 RGB 即可，重新运行
- 改坏了：把 tools/milu-backup.png 拷回 static/characters/milu.png 即可还原
"""
from PIL import Image
import numpy as np
from scipy import ndimage

PNG = r'd:\WeChatFile\tongren\tongren-miniapp\static\characters\milu.png'

# ←←← 你要自己改的地方：眼球颜色（R, G, B, A）。
# 白色 (255, 255, 255, 255)；例如抹茶绿 (168, 203, 158, 255)、黑色描边色 (44, 58, 46, 255)
EYE_COLOR = (255, 255, 255, 255)

im = Image.open(PNG).convert('RGBA')
arr = np.array(im)

# 只在"头部区域"找深色眼球块，避免误伤身体描边
region = arr[2:160, 2:272]
dark = (
    (region[:, :, 0] < 60) & (region[:, :, 1] < 60) &
    (region[:, :, 2] < 60) & (region[:, :, 3] > 0)
)

labels, n = ndimage.label(dark)
changed = 0
for i in range(1, n + 1):
    blob = labels == i
    if blob.sum() >= 300:  # 眼球块面积阈值，跳过细小噪点
        region[blob] = EYE_COLOR
        changed += 1

arr[2:160, 2:272] = region
Image.fromarray(arr, 'RGBA').save(PNG, 'PNG', optimize=True)
print(f'共改了 {changed} 个色块 -> RGB{EYE_COLOR[:3]}，已保存回 milu.png')
