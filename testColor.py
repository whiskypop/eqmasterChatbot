from colorthief import ColorThief

# 打开图片并提取主色
color_thief = ColorThief("C:/Users/v-peipeiwang/Pictures/Screenshots/Screenshot 2024-09-11 212900.png")

# 获取主色，返回 RGB 值
dominant_color = color_thief.get_color(quality=1)

print(dominant_color)
