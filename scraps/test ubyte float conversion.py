import numpy as np

arr1 = np.array([0, 0, 0], dtype=np.ubyte)
arr2 = np.array([0, 0, 1], dtype=np.ubyte)
floated1 = arr1 / 255
floated2 = arr2/255
byted1 = floated1*255
byted2 = floated2*255
print(byted1, byted2)

arr1 = np.array([255, 255, 255], dtype=np.ubyte)
arr2 = np.array([254, 255, 254], dtype=np.ubyte)
floated1 = arr1 / 255
floated2 = arr2/255
byted1 = floated1*255
byted2 = floated2*255
print(byted1, byted2)

while True:
    arr = np.random.randint(0, 255, 3, dtype=np.ubyte)
    floated = arr / 255
    byted = floated * 255
    if not (arr == byted).all():
        raise Exception