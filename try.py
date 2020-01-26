import PIL.Image
# import dlib
import numpy as np
from PIL import ImageFile


im = PIL.Image.open('a.jpg')
im = im.convert('RGB')
a=np.array(im)
print(max(a.shape))