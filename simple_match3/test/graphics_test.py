__author__ = 'magkbdev'

import cocos.layer
import cocos.scene
import cocos.batch
import cocos.sprite

from simple_match3.entity import Aspect
from simple_match3.component import Component
from simple_match3.entity import EntitySystem


class SpriteSheetLayer(object):

    def __init__(self, renderer, resource, order_idx):
        self._name = "default_layer"
        self._renderer = renderer
        self._sprite_sheet = resource
        self._order_index = order_idx
        self._is_hidden = False

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
        self._sprites = []
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
                frame_img = layer.get_frame_image(self.current_state, self.current_frame)
                if frame_img is not None:
                    self._layers_render.append(layer)
                    sprite = cocos.sprite.Sprite(frame_img)
                    sprite.position = self._position
                    self._sprites.append(sprite)

    def render_frame(self):
        for sprite in self._sprites:
            sprite.draw()

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


class RenderSystem(EntitySystem):

    def __init__(self):

        EntitySystem.__init__(self, Aspect.create_aspect_for_all([PositionComponent,
                                                                  SpriteRenderComponent]))

    def render_entity(self, entity):
        render_component = entity.get_component(SpriteRenderComponent)
        position_component = entity.get_component(PositionComponent)

        render_component.position = position_component.get_position()
        render_component.update_frame(1)
        render_component.render_frame()

    def process_entities(self, entities):
        for entity in entities:
            self.render_entity(entity)


if __name__ == "__main__":
    obj = SpriteRenderComponent()