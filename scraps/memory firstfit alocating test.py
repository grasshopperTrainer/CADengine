


arr = list(range(10))
block_pool = [(0, 10)]

def aloc_firstfit(arr, size):
    if size == 0:
        raise
    for i, (sidx, block_size) in enumerate(block_pool):
        leftover = block_size - size
        if 0 <= leftover:
            if leftover == 0:
                block_pool.pop(i)
            else:
                block_pool[i] = (sidx + size, leftover)  # append new free space
            return arr[sidx:sidx+size]
    raise Exception('overflow')

print(aloc_firstfit(arr, 1))
print(aloc_firstfit(arr, 3))
print(aloc_firstfit(arr, 6))

print(block_pool)
