__author__ = 'magkbdev'

from pyglet.gl import *
from pyglet.image import Texture

_get_type_map = {
    int: (GLint, glGetIntegerv),
    float: (GLfloat, glGetFloatv),
}


def get(enum, size=1, type=int):
    type, accessor = _get_type_map[type]
    values = (type*size)()
    accessor(enum, values)
    if size == 1:
        return values[0]
    else:
        return values[:]


class GLObjectContext(object):

    def __init__(self):
        self._stack = list()

    def __enter__(self):
        self._on_enter()
        self._stack.append(get(self._get))
        self.bind(self.id)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.check()
        exit_id = self._stack.pop(-1)
        self.bind(exit_id)
        self._on_exit()

    def _on_enter(self):
        pass

    def _on_exit(self):
        pass

    def check(self):
        pass

    def bind(self, obj_id):
        pass


class TextureContext(GLObjectContext):

    _get = GL_TEXTURE_BINDING_2D

    def __init__(self, pyglet_tex, unit=GL_TEXTURE0):
        GLObjectContext.__init__(self)
        self._pyglet_tex = pyglet_tex
        self._unit = unit

    def bind(self, obj_id):
        glBindTexture(self.target, obj_id)

    def _on_enter(self):
        glPushAttrib(GL_ENABLE_BIT | GL_TEXTURE_BIT)
        glActiveTexture(self._unit)
        glEnable(self.target)

    def _on_exit(self):
        glPopAttrib()

    @property
    def id(self):
        return self._pyglet_tex.id

    @property
    def target(self):
        return self._pyglet_tex.target