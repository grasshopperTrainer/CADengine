import re

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

    __frgm_output_patt = re.compile("""
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
            out                     # keyword
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

    __dtype_patt = re.compile("""([uibd])?([a-zA-Z]+)([\d][.]*)?""")

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
            if d['dtype'].startswith('mat'):
                raise Exception("""using matrix makes location qualifier ambiguous
                please for now, use independed vectors""")

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
                arg_name = d['name']
                dtype = d['dtype']
                loc = int(d['loc'])
                layout = d['layout']
                val = None if not d['val'] else eval(d['val'])

                # check location declaration
                if layout is None:
                    raise SyntaxError(f"{m.group()} <- uniform's layout not declared")

                # check uniquness
                pair = (arg_name, loc)
                for u in unique:
                    if sum([i == j for i, j in zip(pair, u)]) == 1:  # XOR
                        raise ValueError('location and att_name has to be unique')
                unique.add(pair)

                # def val needs additional parsing
                if val:
                    if dtype.startswith('mat'):
                        shape = dtype.replace('mat', '')
                        if shape in ('2', '3', '4'):  # eye set with value
                            parsed_val = np.eye(4)
                            for i in range(int(shape)):
                                parsed_val[i, i] = val
                        else:
                            raise NotImplementedError
                    else:
                        raise NotImplementedError
                    val = parsed_val

                # attribute
                dtype = cls.__translate_dtype(arg_name, dtype)
                if arg_name in args and (args[arg_name][0] != loc or args[arg_name][2] != dtype):
                    raise Exception('attribute contradictory')
                args[d['name']] = (loc, val, dtype)

        if args:
            # align by layout location
            args = sorted(args.values())
            locs, vals, dtype = zip(*args)
            return UfrmSchema(np.dtype(list(dtype)), locs, vals)
        else:
            return None

    __singular_types = {'sampler': 'int32',
                        'bool': 'bool',
                        'int': 'int32',
                        'uint': 'uint32',
                        'float': 'float32',
                        'double': 'float64'}

    @classmethod
    def parse_frgm_outputs(cls, frgm_src, name):
        """
        parse output type and locations

        ! this is a part of automating gl.glDrawBuffers()
        ! fragment outputs must have layout declaration
        :param frgm_src: str, fragment shader source
        :param name: str, name of fragment src
        :return: FrgmOutputSchema,
        """
        unique = set()
        args = {}
        for m in re.finditer(cls.__frgm_output_patt, frgm_src):
            # check layout declaration
            d = m.groupdict()
            if d['layout'] is None:
                raise SyntaxError(f"src:{name}, {m.group()} <- vertex attribute's layout not declared")

            # location
            loc = int(d['loc'])
            pair = (d['name'], loc)
            for u in unique:
                if sum([i == j for i, j in zip(pair, u)]) == 1:  # XOR
                    raise ValueError('location values has to be unique')
            unique.add(pair)

            # attribute
            if d['dtype'].startswith('mat'):
                raise Exception("""using matrix makes location qualifier ambiguous
                        please for now, use independed vectors""")

            dtype = cls.__translate_dtype(d['name'], d['dtype'])
            if d['name'] in args:
                raise Exception('attribute contradictory')
            args[d['name']] = (loc, dtype)

        # align by layout location
        if args:
            args = sorted(args.values())
            locs, dtype = zip(*args)
            return FrgmOutputSchema(np.dtype(list(dtype)), locs)
        else:
            return None

    @classmethod
    def __translate_dtype(cls, name, dtype):
        """
        translate glsl dtype into numpy dtype field

        :param dtype: str, glsl dtype
        :return: (name, dtype, shape), numpy dtype field description
        """
        comp_type, layout_type, shape = re.match(cls.__dtype_patt, dtype).groups()

        if layout_type in cls.__singular_types:  # singular types
            return name, cls.__singular_types[layout_type]

        if shape is not None:  # complex types
            shape = list(map(int, shape.split('x')))
            if layout_type == 'vec':  # vector types
                if comp_type == 'd':
                    layout_type = 'float64'
                elif comp_type == 'i':
                    layout_type = 'int'
                elif comp_type == 'u':
                    layout_type = 'uint'
                elif comp_type == 'b':
                    layout_type = 'bool'
                else:
                    layout_type = 'float32'
                shape = shape[0]
            elif layout_type == 'mat':  # matrix types
                if comp_type == 'd':
                    layout_type = 'float64'
                else:
                    layout_type = 'float32'
                shape = tuple(shape * 2) if len(shape) == 1 else tuple(shape)
            else:
                raise NotImplementedError(name, layout_type)
            return name, layout_type, shape

        raise NotImplementedError
