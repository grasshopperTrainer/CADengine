import re
import numpy as np
import abc

from ckernel.render_context.opengl_context.bffr_cache import BffrCache


class SimpleShdrParser:
    """
    vocabulary:
        parameters : all arguments used in shader including vrtx_attr and uniforms
        vrtx_attr  : vertex attribute, data fed to vertex shader per vertex
        uniforms   :

    Parse parameters from shader

    ? terminology 'lexer' fit better?
    """

    __vrtx_attr_patt = re.compile("""
        ^                           # begining of a line
        (                           # optional layout
            (?P<layout>             # grouping
                [ ]*                # witespace
                    layout          # keyword
                [ ]*                # witespace
                    \([ ]*          # parenthesis
                        location    # keyword
                        [ ]*=[ ]*   # equal sign
                        (?P<loc>    # grouping
                            \d+     # anonymous index
                        )
                    [ ]*\)
            )
        )?
        [ ]*                        # witespace
            in                      # keyword
        [ ]+                        # one or more witespace
            (?P<dtype>              # grouping
                [a-zA-Z]+[\w]*      # type name starting with alph
            )
        [ ]+                        # one or more witespace
            (?P<name>               # grouping
                [a-zA-Z]+[\w]*      # var name starting with alph
            )
    ;                       # end of statement
        """, re.VERBOSE | re.MULTILINE)
    __layout_ufrm_patt = re.compile("""
    ^                               # begining of a line
    (                               # optional layout
        (?P<layout>                 # grouping
            [ ]*                    # witespace
                layout              # keyword
            [ ]*                    # witespace
                \([ ]*              # location value
                    location        # keyword
                    [ ]*=[ ]*       # equal sign
                    (?P<loc>        # grouping
                        \d+         # anonymous index
                    )
                [ ]*\)
        )
    )?
    [ ]*                            # witespace
        uniform                     # keyword
    [ ]+                            # one or more witespace
        (?P<dtype>                  # grouping
            [a-zA-Z]+[\w]*          # type name starting with alph
        )
    [ ]+                            # one or more witespace
        (?P<name>                   # grouping
            [a-zA-Z]+[\w]*          # var name starting with alph
        )
        (                           # optional default val assignment
            [ ]*=[ ]*               # equal sign
            [a-zA-Z]+[\w]*          # type
                [ ]*\([ ]*          # parenthesis
                    (?P<val>        # grouping
                        .*          # value
                    )
                [ ]*\)[ ]*
        )?
;                       # end of statement
    """, re.VERBOSE | re.MULTILINE)
    __dtype_patt = re.compile('([a-zA-Z]*)([\d].*)?')

    @classmethod
    def parse_vrtx_shdr(cls, src):
        pass

    @classmethod
    def __parse_vrtx_attrs(cls, src):
        """
        parse vertex attribues into dtype

        ! uniforms must have layout declaration
        :param src: str, vertex shader source
        :return: (numpy structured dtype, locations)
        """
        args = []
        # check layout declaration and arguments
        for m in re.finditer(cls.__vrtx_attr_patt, src):
            d = m.groupdict()
            if d['layout'] is None:
                raise SyntaxError(f"{m.group()} <- vertex attribute's layout not declared")
            args.append([int(d['loc']), cls.__translate_dtype(d['name'], d['dtype'])])
        # align by layout location
        args.sort()
        locs, dtype = zip(*args)
        return np.dtype(list(dtype)), locs

    @classmethod
    def __parse_uniforms(cls, src):
        """
        parse uniforms into dtype

        ! uniforms must have layout declaration
        :param src: str, vertex shader source
        :return: (numpy structured dtype, locations, default values)
        """
        args = []
        # check layout declaration and arguments
        for m in re.finditer(cls.__layout_ufrm_patt, src):
            d = m.groupdict()
            if d['layout'] is None:
                raise SyntaxError(f"{m.group()} <- uniform's layout not declared")
            loc = int(d['loc'])
            dtype = cls.__translate_dtype(d['name'], d['dtype'])
            val = eval(d['val'])
            args.append([loc, dtype, val])
        # align by layout location
        args.sort()
        locs, dtype, vals = zip(*args)
        return np.dtype(list(dtype)), locs, vals

    @classmethod
    def validate_vrtx_shdr(cls, src):
        """
        check for enforced layout principle in src

        :param src: str, vertex shader source
        :return: (VrtxAttrs, Uniforms)
        """
        return VrtxAttrSkema(*cls.__parse_vrtx_attrs(src)), UfrmSkema(*cls.__parse_uniforms(src))

    @classmethod
    def __translate_dtype(cls, name, dtype):
        """
        translate glsl dtype into numpy dtype field

        :param dtype: str, glsl dtype
        :return: (name, dtype, shape), numpy dtype field-like
        """
        dtype, shape = re.match(cls.__dtype_patt, dtype).groups()
        if shape is None:
            shape = (1,)
        else:
            shape = shape.replace('x', ',')
            if 'vec' in dtype:
                if dtype.startswith('d'):
                    dtype = 'f8'
                elif dtype.startswith('i'):
                    dtype = 'int'
                elif dtype.startswith('u'):
                    dtype = 'uint'
                else:
                    dtype = 'f4'
                shape = int(shape)

            elif 'mat' in dtype:
                if dtype.startswith('d'):
                    dtype = 'f8'
                else:
                    dtype = 'f4'
                shape = eval(f"({shape}, {shape})" if len(shape) == 1 else f"({shape})")

            else:
                raise NotImplementedError(name, dtype)
        # field description
        return name, dtype, shape


class _GLSLParamSkema:
    pass


class VrtxAttrSkema(_GLSLParamSkema):
    """
    Vertex attribute skema
    """
    def __init__(self, dtype, locs):
        self.__dtype = dtype
        self.__locs = locs

    def __str__(self):
        return f"<{self.__class__.__name__}: {self._dtype}>"

    def create_bffr_cache(self, size):
        """
        create buffer cache for vertex attributes

        :param size: size o
        :return:
        """
        cache = BffrCache(self.__dtype, size)
        return cache


class UfrmSkema(_GLSLParamSkema):
    """
    Uniform skema

    """
    def __init__(self, dtype, locs, def_val):
        self.__dtype = dtype
        self.__locs = locs
        self.__def_val = def_val

    def __str__(self):
        return f"<{self.__class__.__name__}: {self._dtype}>"

    def create_bffr_cache(self, size):
        """
        create buffer cache for uniform values

        :return:
        """
        cache = BffrCache(self.__dtype, size)
        for name, val in zip(self.__dtype.fields, self.__def_val):
            cache.array[name][...] = val
        return cache
