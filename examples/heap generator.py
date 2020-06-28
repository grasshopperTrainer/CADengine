import heapq

def gen():
    h = [123, 2,3,3,4,5,12,3,5,1,12,2,3,2]
    # for i in h:
    #     yield i

# g = gen()
# for i in g:
#     print(i)
a = {1,2,3}
b = [4,2,1]
a.update(b)
print(a)
# try:
#     while True:
#         if next(g) == 12:
#             print('twelve')
#             break
# except StopIteration as e:
#     print('end iter')
# else:
#     print('else')