from PIL import Image
import cv2
from cv2 import dnn_superres

def resize_to_9_16(image):
    height, width, _ = image.shape
    target_ratio = 9 / 16

    if width / height > target_ratio:
        new_width = width
        new_height = int(width / target_ratio)
    else:
        new_height = height
        new_width = int(height * target_ratio)
    return cv2.resize(image, (new_width, new_height))

for i in range(1, 6):
    cv2.imwrite(f"sample_{i}_resized.jpg", resize_to_9_16(cv2.imread(f'sample_{i}.jpg')))