import os
import weakref as wr
import numpy as np
from numbers import Number
import ctypes

from global_tools.enum import enum
import ckernel.render_context.opengl_context.opengl_hooker as gl
import ckernel.render_context.opengl_context.meta_entities as meta
from ckernel.render_context.opengl_context.ogl_entities import _FrameBffr
from ckernel.render_context.opengl_context.context_stack import get_current_ogl

import gkernel.dtype.geometric as gt
import gkernel.dtype.nongeometric.matrix as mx
import gkernel.color as clr

from wkernel.devices.render._base import RenderDevice, RenderDeviceManager
from global_tools.lazy import lazyProp
from ckernel.render_context.opengl_context.constant_enum import DrawTargetFormats as DTF
from ckernel.render_context.opengl_context.constant_enum import TextureTargets as TT


class FrameRenderer:
    # program for drawing quad
    __THIS_PATH = os.path.dirname(__file__)
    __quad_prgrm = meta.MetaPrgrm(vrtx_path=os.path.join(__THIS_PATH, 'quad_vrtx_shdr.glsl'),
                                  frgm_path=os.path.join(__THIS_PATH, 'quad_frgm_shdr.glsl'))
    __pane_prgrm = meta.MetaPrgrm(vrtx_path=os.path.join(__THIS_PATH, 'pane_vrtx_shdr.glsl'),
                                  frgm_path=os.path.join(__THIS_PATH, 'pane_frgm_shdr.glsl'))
    __pane_depth_prgrm = meta.MetaPrgrm(vrtx_path=os.path.join(__THIS_PATH, 'pane_vrtx_shdr.glsl'),
                                        frgm_path=os.path.join(__THIS_PATH, 'pane_depth_frgm_shdr.glsl'))

    def __init__(self):
        # quad set
        self.__quad_vbo = self.__quad_prgrm.vrtxattr_schema.create_vrtx_bffr()
        self.__quad_block = self.__quad_vbo.cache.request_block(size=4)
        self.__quad_block['tex_coord'] = (0, 0), (1, 0), (1, 1), (0, 1)
        self.__quad_vao = meta.MetaVrtxArry(self.__quad_vbo)
        # pane set
        self.__pane_vbo = self.__pane_prgrm.vrtxattr_schema.create_vrtx_bffr()
        self.__pane_block = self.__pane_vbo.cache.request_block(size=4)
        self.__pane_block['tex_coord'] = (0, 0), (1, 0), (1, 1), (0, 1)
        self.__pane_vao = meta.MetaVrtxArry(self.__pane_vbo)
        # pane depth set
        self.__pane_depth_vbo = self.__pane_depth_prgrm.vrtxattr_schema.create_vrtx_bffr()
        self.__pane_depth_block = self.__pane_depth_vbo.cache.request_block(size=4)
        self.__pane_depth_block['tex_coord'] = (0, 0), (1, 0), (1, 1), (0, 1)
        self.__pane_depth_vao = meta.MetaVrtxArry(self.__pane_depth_vbo)

    def render_pane_space(self, texture, txtr_domain, pane_domain, pane_z):
        """
        render frame's given attachment on pane space

        :param texture: render source
        :param pdomain_x: (-1.~1., -1.~1.), pane space x domain
        :param pdomain_y: (-1.~1., -1.~1.), pane space y domain
        :param pane_z: -1.~1., pane space z value, -1 closest
        :param tdomain_x: (float, float), texture space x domain
        :param tdomain_y: (float, float), texture space y domain
        :return:
        """
        # update
        xs, xe, ys, ye = txtr_domain
        self.__pane_block['tex_coord'] = (xs, ys), (xe, ys), (xe, ye), (xs, ye)
        xs, xe, ys, ye = pane_domain
        self.__pane_block['coord'] = (xs, ys, pane_z), (xe, ys, pane_z), (xe, ye, pane_z), (xs, ye, pane_z)
        self.__pane_vbo.push_cache()
        # render
        with texture:
            with self.__pane_vao:
                with self.__pane_prgrm:
                    gl.glDrawArrays(gl.GL_QUADS, 0, 4)

    def render_pane_space_depth(self, color_txtr, depth_txtr, txtr_domain, pane_domain):
        # update
        xs, xe, ys, ye = txtr_domain
        self.__pane_depth_block['tex_coord'] = (xs, ys), (xe, ys), (xe, ye), (xs, ye)
        xs, xe, ys, ye = pane_domain
        self.__pane_depth_block['coord'] = (xs, ys, 0), (xe, ys, 0), (xe, ye, 0), (xs, ye, 0)
        self.__pane_depth_vbo.push_cache()

        with color_txtr.as_unit(0), depth_txtr.as_unit(1):  # using texture as unit 0, 1
            with self.__pane_depth_vao:
                with self.__pane_depth_prgrm:
                    # update uniforms
                    self.__pane_depth_prgrm.uniforms['myTexture'] = 0
                    self.__pane_depth_prgrm.uniforms['myDepth'] = 1
                    self.__pane_depth_prgrm.push_uniforms()

                    gl.glDrawArrays(gl.GL_QUADS, 0, 4)

    def render_world_space(self, texture, quad_pos, domain_x, domain_y):
        # update vrtx attributes
        (xs, xe), (ys, ye) = domain_x, domain_y
        self.__quad_block['tex_coord'] = (xs, ys), (xe, ys), (xe, ye), (xs, ye)
        self.__quad_block['coord'] = quad_pos
        self.__quad_vbo.push_cache()
        # render
        with texture:
            with self.__quad_vao:
                with self.__quad_prgrm:
                    # update uniforms
                    camera = get_current_ogl().manager.window.devices.cameras.current
                    self.__quad_prgrm.uniforms['PM'] = camera.body.PM
                    self.__quad_prgrm.uniforms['VM'] = camera.tripod.VM
                    self.__quad_prgrm.uniforms['MM'] = [[1, 0, 0, 0],
                                                        [0, 1, 0, 0],
                                                        [0, 0, 1, 0],
                                                        [0, 0, 0, 1]]
                    self.__quad_prgrm.push_uniforms()
                    gl.glDrawArrays(gl.GL_QUADS, 0, 4)


class Frame(RenderDevice):

    def __init__(self, manager, frame_bffr, width, height):
        super().__init__(manager)
        self.__frame_bffr = frame_bffr
        self.__size = width, height
        # for drawing
        self.__renderer = FrameRenderer()

    def __enter__(self):
        """
        1. bind frame buffer
        2. record current device
        :return:
        """
        self.__frame_bffr.bind()  # binding for ogl operations
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        if self.get_current() is not self:
            self.get_current().frame_bffr.bind()

    def __str__(self):
        return f"<Frame {self.__size}>"

    @property
    def frame_bffr(self) -> meta.MetaFrameBffr:
        return self.__frame_bffr

    @property
    def size(self):
        """
        size of frame buffer

        ! all internal components also have the same size
        :return:
        """
        return self.__size

    def render_pane_space(self, tid, txtr_domain=(0, 1, 0, 1), pane_domain=(-1, 1, -1, 1), pane_z=0):
        """
        render frame's given attachment on pane space

        :param tid: texture id, e.g.
                    0, 1 - integers for color attachment
                    'd' - depth attachment
                    'ds' - depth stencil attachment
        :param txtr_domain: (f, f, f, f), texture space x0,y0, x0,y0 domain
        :param pane_domain: (-1.~1., -1.~1., -1.~1., -1.~1.), texture space x0,y0, x1,y1 domain
        :param pane_z: -1.~1., pane space z value, -1 closest
        :param with_depth: bool, render with current frame buffer's depth texture
        :return:
        """
        texture = self.__frame_bffr.get_attachment(tid)
        self.__renderer.render_pane_space(texture, txtr_domain, pane_domain, pane_z)

    def render_pane_space_depth(self, tid, txtr_domain=(0, 1, 0, 1), pane_domain=(-1, 1, -1, 1)):
        """
        render frame's given attachment on pane space with depth texture

        :param tid: texture id, e.g.
                    0, 1 - integers for color attachment
                    'd' - depth attachment
                    'ds' - depth stencil attachment
        :param txtr_domain: (f, f, f, f), texture space x0,y0, x0,y0 domain
        :param pane_domain: (-1.~1., -1.~1., -1.~1., -1.~1.), texture space x0,y0, x1,y1 domain
        :return:
        """
        color_txtr = self.__frame_bffr.get_attachment(tid)
        depth_txtr = self.__frame_bffr.get_attachment('d')
        self.__renderer.render_pane_space_depth(color_txtr, depth_txtr, txtr_domain, pane_domain)

    def render_world_space(self, aid, pln: gt.Pln, width, height, tdomain_x=(0, 1), tdomain_y=(0, 1)):
        """
        render frame's given attachment on world coordinate system

        :param aid: int, color attachment id
        :param pln: Pln, plane to render at
        :param width: Number, width of render area
        :param height: Number, height of render area
        :param tdomain_x: (float, float), texture space x domain
        :param tdomain_y: (float, float), texture space y domain
        :return:
        """
        if not isinstance(aid, int):
            raise TypeError
        if not isinstance(pln, gt.Pln):
            raise TypeError
        if any(not isinstance(d, Number) for d in (width, height)):
            raise TypeError

        # calculate quad position
        # coverage represented as polyline then as coordinates
        w, h = self.__size
        quad_pos = gt.Plin((0, 0, 0), (w, 0, 0), (w, h, 0), (0, h, 0))
        sm = mx.ScaleMat(x=width / w, y=height / h, z=1)
        quad_pos = sm * quad_pos
        quad_pos = pln.orient(obj=quad_pos, ref_pln=gt.Pln()).T

        texture = self.__frame_bffr.get_attachment(aid)
        self.__renderer.render_world_space(texture, quad_pos, tdomain_x, tdomain_y)

    def pick_pixel(self, tid, pos, size) -> clr.Clr:
        """
        pick texture pixel of a given attachment id, position

        :param tid: int, color attachment id
        :param pos: (x, y), pixel coordinate
                    int   - absolute texture coordinate
                    float - parameterized
        :param size: (width, height) picking area
                    int   - absolute pixel area
                    float - parameterized relative to texture size
        :return:
        """
        # parse pos expression
        texture = self.frame_bffr.get_attachment(tid)
        if isinstance(pos, gt.Vec):
            pos = pos.xy
        x, y = [int(v * b) if isinstance(v, float) else v for v, b in zip(pos, texture.size)]

        # parse size expression
        if isinstance(pos, gt.Vec):
            size = size.xy
        w, h = [int(v * b) if isinstance(v, float) else v for v, b in zip(size, texture.size)]

        # get source
        if isinstance(tid, int):
            src = eval(f"gl.GL_COLOR_ATTACHMENT{tid}")
        elif tid == 'd':
            src = eval(gl.GL_DEPTH_ATTACHMENT)
        elif tid == 'ds':
            src = eval(gl.GL_DEPTH_STENCIL_ATTACHMENT)
        else:
            raise

        # get format
        if DTF.COLOR.RG.has_member(texture.iformat):
            frmt = gl.GL_RED
        elif DTF.COLOR.RG.has_member(texture.iformat):
            frmt = gl.GL_RG
        elif DTF.COLOR.RGB.has_member(texture.iformat):
            frmt = gl.GL_RGB
        elif DTF.COLOR.RGBA.has_member(texture.iformat):
            frmt = gl.GL_RGBA
        else:
            raise NotImplementedError

        gl.glReadBuffer(src)
        # is returning raw array okay?
        return gl.glReadPixels(x, y, w, h, frmt, gl.GL_FLOAT)

    def pick_texture_area(self, aid, xdomain, ydomain, parameterized):
        """
        pick value of given texture area

        :param aid:
        :param xdomain:
        :param ydomain:
        :param parameterized:
        :return:
        """
        raise NotImplementedError

    def clear(self, r=0, g=0, b=0, a=1):
        """
        clear all

        :param r: (0 ~ 1.0), float for red
        :param g: (0 ~ 1.0), float for green
        :param b: (0 ~ 1.0), float for blue
        :param a: (0 ~ 1.0), float for alpha
        :param color: bool, flag clean color
        :param depth: bool, flag clean depth
        :param stencil: bool, flag clean stencil
        :return:
        """

        gl.glClearColor(r, g, b, a)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

    def clear_texture(self, id, r, g, b, a):
        """
        clear texture of given attachment id

        :param id: int, color attachment id
        :param r: (0 ~ 1.0), float for red
        :param g: (0 ~ 1.0), float for green
        :param b: (0 ~ 1.0), float for blue
        :param a: (0 ~ 1.0), float for alpha
        :return:
        """
        texture = self.frame_bffr.get_attachment(id)
        color = np.array((r, g, b, a), dtype=np.float32)
        gl.glClearTexImage(texture.get_concrete(), 0, texture.iformat, gl.GL_FLOAT, color)

    def clear_depth(self):
        """
        clear depth

        :return:
        """
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT)

    def clear_stencil(self):
        """
        clear stencil

        :return:
        """
        raise NotImplementedError


class _Frame(Frame):
    """
    Just a type notifier for IDE
    """

    def __enter__(self) -> Frame:
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class FrameManager(RenderDeviceManager):

    def __init__(self, device_master):
        super().__init__(device_master)
        # default device just binds 0 to get back to glfw provided buffer
        # ! assigning concrete frame buffer
        ww, wh = self.window.glyph.size
        frame = Frame(self, _FrameBffr(0, gl.GL_FRAMEBUFFER), ww, wh)
        self._appendnew_device(frame)
        self.master.tracker.stack.set_base_entity(frame)

    def __getitem__(self, item) -> _Frame:
        """
        just to indicate return type
        :param item:
        :return:
        """
        return super().__getitem__(item)

    @property
    def device_type(self):
        return Frame

    @property
    def factory(self):
        return FrameFactory(self)


class FrameFactory:
    @enum
    class TXTR:
        TRGT = TT
        CLR_FRMT = DTF.COLOR
        DEPTH_FRMT = DTF.NONECOLOR.DEPTH

    @enum
    class RNDR:
        DEPTH = DTF.NONECOLOR.DEPTH
        DEPTH_STENCIL = DTF.NONECOLOR.DEPTH_STENCIL

    # TODO: fix color attachment allocation
    def __init__(self, manager):
        self.__manager = wr.ref(manager)
        self.__size = None
        self.__tids = set()
        self.__textures_prop = []
        self.__render_buffer_prop = []

    def set_size(self, width, height):
        """
        make fb components have equal size

        :param width: int, pixel width
        :param height: int, pixel height
        :return:
        """
        if any(not isinstance(i, int) for i in (width, height)):
            raise TypeError
        self.__size = width, height

    def append_color_texture(self, target, format, lid):
        """
        append texture for color attachment

        :param target: target e.g. TEXTURE.TARGET.TWO_D
        :param format: internal format
        :param lid: int, color attachment id
        :return:
        """
        # guess texture id if not given
        if not self.TXTR.CLR_FRMT.has_member(format):
            raise TypeError
        if not isinstance(lid, int):
            raise TypeError

        # check uniqueness
        if lid in self.__tids:
            raise ValueError

        # append
        self.__textures_prop.append((target, format, lid))
        self.__tids.add(lid)
        return self

    def append_depth_texture(self, target, format):
        """
        append texture for depth

        :param target: target e.g. TEXTURE.TARGET.TWO_D
        :param format: internal format
        :return:
        """
        if format not in DTF.NONECOLOR.DEPTH:
            raise TypeError

        # check uniqueness
        tid = 'd'
        if tid in self.__tids:
            raise ValueError

        # append
        self.__textures_prop.append((target, format, tid))
        self.__tids.add(tid)
        return self

    def append_depth_stencil_texture(self, target, format):
        raise NotImplementedError

    def set_render_buffer(self, format, lid):
        """
        add render buffer

        :return:
        """
        if not (isinstance(lid, int) or lid in ('d', 'ds')):
            raise ValueError("location id should be int for color att. or one of 'd', 'ds' for depth")
        self.__render_buffer_prop.append((format, lid))

    def create(self) -> Frame:
        """
        create new meta frame

        :return:
        """
        if not (self.__textures_prop or self.__render_buffer_prop):
            raise ValueError('not enough properties given')

        if not self.__size:
            raise ValueError('texture size not set')

        # textures
        w, h = self.__size
        locs = []
        textures = []
        for t, f, i in self.__textures_prop:
            if i in locs:
                raise ValueError('color attachment location has to be unique')
            locs.append(i)
            textures.append(meta.MetaTexture(target=t, iformat=f, width=w, height=h))

        # render buffers
        # ! currently only one render buffer supported
        render_bffrs = []
        for f, i in self.__render_buffer_prop:
            if i in locs:
                raise ValueError('color attachment location has to be unique')
            locs.append(i)
            render_bffrs.append(meta.MetaRenderBffr(iformat=f, width=w, height=h))

        frame_bffr = meta.MetaFrameBffr(*textures, *render_bffrs, lid=locs)

        manager = self.__manager()
        frame = Frame(manager, frame_bffr, w, h)
        manager._appendnew_device(frame)
        return frame
