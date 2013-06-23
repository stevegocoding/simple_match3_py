from component import Component
from gl_utils import TextureContext
from pyglet.sprite import SpriteGroup
import pyglet.gl as gl


class SpriteGroupContext(SpriteGroup):

    def __init__(self,
                 texture,
                 frame_buffer,
                 shader,
                 blend_src=gl.GL_SRC_ALPHA, blend_dest=gl.GL_ONE_MINUS_SRC_ALPHA,):

        super(SpriteGroupContext, self).__init__(texture, blend_src, blend_dest)

        self._tex_context = TextureContext(self.texture)
        self._frame_buffer = frame_buffer
        self._shader = shader

    def set_state(self):
        self._frame_buffer.set_state()
        self._shader.set_state()
        self._tex_context.set_state()

    def unset_state(self):
        self._frame_buffer.unset_state()
        self._shader.unset_state()
        self._tex_context.unset_state()


class GPURenderContext(object):
    pass


class GPURenderComponent(Component):

    def create_gpu_resource(self, render_context):
        pass


