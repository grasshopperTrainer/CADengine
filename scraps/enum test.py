from global_tools.enum import enum

@enum
class K:
    A = 'a'
    B = 'a'
    C = 'c'
    D = None

    @enum
    class SUBE:
        A = 'a'
        B = 'b'
        C = 'c'
