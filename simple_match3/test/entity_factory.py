__author__ = 'magkbdev'

import cocos.sprite

from pyglet.sprite import Sprite

from simple_match3.managers import EntityManager
from simple_match3.entity import EntityRecord
from simple_match3.component import Component
from simple_match3.resource import ResourceManagerSingleton


class SpriteSheetLayer(object):

    def __init__(self, renderer, resource, order_idx):
        self._name = "default_layer"
        self._renderer = renderer
        self._sprite_sheet = resource
        self._order_index = order_idx
        self._is_hidden = False

        image = self.get_frame_image(self._renderer.current_state, self._renderer.current_frame)
        self._sprite = Sprite(image)

    def get_frames_count(self, state):
        if self._sprite_sheet is not None:
            return self._sprite_sheet.get_frames_count(state)
        else:
            return 0

    def get_frame_image(self, state, frame):
        if self._sprite_sheet is not None:
            frame_img = self._sprite_sheet.get_frame_image(state, frame)
            return frame_img
        else:
            return None

    def draw(self):
        image = self.get_frame_image(self._renderer.current_state, self._renderer.current_frame)
        pos = self._renderer.position

        if image is not None:
            self._sprite._set_image(image)
            self._sprite.position = pos
            self._sprite.draw()

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self.name = value

    @property
    def order_index(self):
        return self._order_index

    @property
    def is_hidden(self):
        return self._is_hidden


class SpriteRenderComponent(Component):

    def __init__(self, spritesheet_resources=None):
        Component.__init__(self)

        self._current_state = "default"
        self._frame_index = 0
        self._max_frames = 0
        self._layers = []
        self._layers_render = []
        self._loop = True
        self._animation_percent = 0
        self._position = (0, 0)

    def create_layer(self, resource, order_index):
        layer = SpriteSheetLayer(self, resource, order_index)
        self._layers.append(layer)
        self.sort_layers()

    def reset_frame_data(self):
        self._sprites = []
        self._max_frames = 0

    def reset_animation(self):
        self._frame_index = 0
        self._animation_percent = 0

    def update_frame(self, animation_ticks):
        self.reset_frame_data()
        self._max_frames = self.get_animation_frames_count()

        ticks = animation_ticks
        while ticks > 0:
            ticks -= 1
            self._frame_index += 1
            if self._frame_index >= self._max_frames:
                if self._loop is not True:
                    self._frame_index = self._max_frames - 1
                else:
                    self._frame_index = 0
                self._animation_percent = 100

        # Update the animation percentage
        percent = (self._frame_index / self._max_frames) * 100 if self._max_frames > 1 else 100
        if percent > self._animation_percent:
            self._animation_percent = percent

        # Build the array of images to draw in current state
        for layer in self._layers:
            if layer.is_hidden is not True:
                self._layers_render.append(layer)

    def render_frame(self):
        for layer in self._layers_render:
            layer.draw()

        # clear the list of the layers to render
        self._layers_render = []

    def sort_layers(self):
        if len(self._layers) > 1:
            self._layers.sort(key=lambda x: x.order_index)

    def get_animation_frames_count(self):
        max_frames = 0

        for layer in self._layers:
            if layer.is_hidden is not True:
                total_frames = layer.get_frames_count(self.current_state)

                if max_frames < total_frames:
                    max_frames = total_frames

        return max_frames

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, state):
        if self.current_state == state:
            return

        self._current_state = state
        self._frame_index = 0
        self._animation_percent = 0

    @property
    def current_frame(self):
        return self._frame_index

    @property
    def max_frames(self):
        return self._max_frames

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value


class PositionComponent(Component):

    def __init__(self):
        Component.__init__(self)

    def get_position(self):
        return 100, 100


class EntityFactory(object):
    def __init__(self):
        pass

    @staticmethod
    def create_blue_crystal(world, pos):
        entity = EntityRecord(world, world.get_manager_by_type(EntityManager).generate_id())

        pos_component = PositionComponent()
        entity.attach_component(pos_component)

        sprite_component = SpriteRenderComponent()
        sprite_resource = ResourceManagerSingleton.instance().find_resource("rotating_crystals")

        sprite_component.current_state = "crystal_blue"
        sprite_component.create_layer(sprite_resource, 0)
        entity.attach_component(sprite_component)

        return entity