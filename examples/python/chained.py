# class MemberIterator:
#     def __init__(self):
#         raise NotImplementedError
#     # def __next__(self):
#     #     raise NotImplementedError
#     def __iter__(self):
#         raise NotImplementedError
#     def __len__(self):
#         raise NotImplementedError
#
# class I(MemberIterator):
#
#     def __init__(self, iterator, next):
#         self._iterator = iterator
#         self._next = next
#
#     def __iter__(self):
#         for i in self._iterator:
#             yield i
#         for i in self._iterator(self._next):
#             yield i
#
#
# class TypeIterator(MemberIterator):
#
#     def __init__(self, iterator, typ):
#         self._iterator = iterator
#         self._typ = typ
#
#     def __iter__(self):
#         for i in self._iterator:
#             if isinstance(i, self._typ):
#                 yield i
#
#     def __call__(self, member):
#         self._iterator = self._iterator(member)
#         return self
#         # return self.__class__(self._iterator.__call__(member), self._typ)
#
# class ParentIterator(MemberIterator):
#
#     def __init__(self, start_at):
#         self._start_at = start_at
#
#     def __iter__(self):
#         for parent in self._start_at._l:
#             yield parent
#
#     def __call__(self, start_at):
#         return self.__class__(start_at)
#
# class ChildrenIterator(MemberIterator):
#
#     def __init__(self, start_at):
#         self._start_at = start_at
#
#     def __iter__(self):
#         for child in self._start_at._l:
#             yield child
#
#     def __call__(self, start_at):
#         self._start_at = start_at
#
#
# class A:
#     def __init__(self, l):
#         self._l = l
#
#
# a = A([1,'k',2,'q', 'l', 3])
# b = A(('a',10,'b',11,'c'))
# k = TypeIterator(ParentIterator(a), str)
# for i in k:
#     print(i)
#     if i == 'k':
#         k(b)
#
#     # k(b)
#     # for i in k:
#     #     print(i)
# print(callable(TypeIterator))

l = [1,2,3,'k','s',4,'d',5]

def a(iterable):
    for i in iterable:
        yield i

def b(iterable, typ):
    for i in iterable:
        if isinstance(i, typ):
            yield i

def it(self, iterable):
    for i in iterable(self):
        yield i

for i in a(l):
    print(i)
print()
for i in b(l, str):
    print(i)
print()

for i in it(l, b(a, int)):
    print(i)