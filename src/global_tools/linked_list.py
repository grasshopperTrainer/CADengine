# """
# this is bad for binary search...
# """
#
# class DoublyLinkedList:
#     def __init__(self, is_doubly=False):
#         self.__is_doubly = is_doubly
#         self.__head = self.__Node(None)
#         self.__tail = self.__head
#         self.__len = 0
#
#     def __len__(self):
#         return self.__len
#
#     def __getitem__(self, item):
#         if not isinstance(item, int):
#             raise TypeError
#         # check which way is shorter
#         d = self.__len - item
#         if d < 1:
#             raise IndexError
#         # search backward
#         if d <= item:
#             node = self.__tail
#             for _ in range(d-1):
#                 node = node.left()
#             return node.val
#         else:
#             node = self.__head
#             for _ in range(item):
#                 node = node.right()
#             return node.val
#
#     def append(self, val):
#         """
#         append value
#
#         :param val: value to add
#         :return:
#         """
#         node = self.__Node(val)
#         node.set_left(self.__tail)
#         self.__tail = node
#         self.__tail.set_right(node)
#         self.__len += 1
#
#
#     class __Node:
#         def __init__(self, val):
#             self.__val = val
#             self.__left = None
#             self.__right = None
#
#         @property
#         def left(self):
#             return self.__left
#
#         @property
#         def right(self):
#             return self.__right
#
#         @property
#         def val(self):
#             return self.__right
#
#         def set_left(self, node):
#             if not isinstance(node, self.__class__):
#                 raise TypeError
#             self.__left = node
#
#         def set_right(self, node):
#             if not isinstance(node, self.__class__):
#                 raise TypeError
#             self.__right = node
#
#         def iter_backward(self):
#             """
#             iter nodes backward including self
#
#             :return:
#             """
#             node = self
#             while not node.__left.is_head:
#                 yield node
#                 node = self.__left
#
#         def iter_forward(self):
#             """
#             iter nodes forward including self
#
#             :return:
#             """
#             node = self
#             while not node.__right.is_tail:
#                 yield node
#                 node = self.__right
#
#         @property
#         def left(self):
#             return self.__left
#
#         @property
#         def right(self):
#             return self.__right
#
#         @property
#         def is_tail(self):
#             return self.__right is None
#
#         @property
#         def is_head(self):
#             return self.__left is None