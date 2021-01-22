import re
import numpy as np

from .schemas import *


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
    def parse_vrtx_attrs(cls, vrtx_shdr_src):
        """
        parse vertex attribues into dtype

        ! vertex attributes must have layout declaration
        :param vrtx_shdr_src: str, vertex shader sources
        :return: (numpy structured dtype, locations)
        """
        unique = set()
        args = {}
        for m in re.finditer(cls.__vrtx_attr_patt, vrtx_shdr_src):
            # check layout declaration
            d = m.groupdict()
            if d['layout'] is None:
                raise SyntaxError(f"{m.group()} <- vertex attribute's layout not declared")

            # location
            loc = int(d['loc'])
            pair = (d['name'], loc)
            for u in unique:
                if sum([i == j for i, j in zip(pair, u)]) == 1:  # XOR
                    raise ValueError('location values has to be unique')
            unique.add(pair)

            # attribute
            dtype = cls.__translate_dtype(d['name'], d['dtype'])
            if d['name'] in args:
                raise Exception('attribute contradictory')
            args[d['name']] = (loc, dtype)

        # align by layout location
        if args:
            args = sorted(args.values())
            locs, dtype = zip(*args)
            return VrtxAttrSchema(np.dtype(list(dtype)), locs)
        else:
            return None

    @classmethod
    def parse_uniforms(cls, *sources):
        """
        parse uniforms into dtype

        ! uniforms must have layout declaration
        :param sources: (str, ...), vertex shader sources
        :return: (numpy structured dtype, locations, default values)
        """
        unique = set()
        args = {}
        for src in sources:
            for m in re.finditer(cls.__layout_ufrm_patt, src):
                # check layout declaration
                d = m.groupdict()
                if d['layout'] is None:
                    raise SyntaxError(f"{m.group()} <- uniform's layout not declared")

                # location
                loc = int(d['loc'])
                pair = (d['name'], loc)
                for u in unique:
                    if sum([i == j for i, j in zip(pair, u)]) == 1: # XOR
                        raise ValueError('location values has to be unique')
                unique.add(pair)

                # value
                if d['val'] is not None:
                    val = eval(d['val'])
                else:
                    val = None

                # attribute
                dtype = cls.__translate_dtype(d['name'], d['dtype'])
                if d['name'] in args and args[d['name']] != (loc, val, dtype):
                    raise Exception('attribute contradictory')
                args[d['name']] = (loc, val, dtype)

        if args:
            # align by layout location
            args = sorted(args.values())
            locs, vals, dtype = zip(*args)
            return UfrmSchema(np.dtype(list(dtype)), locs, vals)
        else:
            return None

    @classmethod
    def __translate_dtype(cls, name, dtype):
        """
        translate glsl dtype into numpy dtype field

        :param dtype: str, glsl dtype
        :return: (name, dtype, shape), numpy dtype field-like
        """
        dtype, shape = re.match(cls.__dtype_patt, dtype).groups()
        if shape is None:
            if dtype == 'bool':
                dtype = 'bool'
            elif dtype == 'int':
                dtype = 'int'
            elif dtype == 'uint':
                dtype = 'uint'
            elif dtype == 'float':
                dtype = 'f4'
            elif dtype == 'double':
                dtype = 'f8'
            else:
                raise TypeError
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

