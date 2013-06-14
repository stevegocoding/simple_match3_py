__author__ = 'magkbdev'

import cocos.director
import cocos.layer
import cocos.scene
import cocos.batch
import cocos.sprite

import pyglet.resource

from simple_match3.resource import GameAssetArchiveLoader
from simple_match3.resource import ResourceManager
from simple_match3.entity import Aspect
from simple_match3.entity import EntitySystem
from simple_match3.world import EntityWorld
from simple_match3.managers import EntityManager

from entity_factory import PositionComponent
from entity_factory import SpriteRenderComponent


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


class GraphicsTestLayer(cocos.layer.Layer):

    def __init__(self, world):
        super(GraphicsTestLayer, self).__init__()

        self._world = world

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def visit(self):
        pass

    def draw(self):
        pass


from entity_factory import EntityFactory


def initialize_system():
    pyglet.resource.path = ["assets", "assets/gfx", "assets/sound"]
    pyglet.resource.reindex()

    asset_loader = GameAssetArchiveLoader()
    asset_loader.level("test_level")


def create_game_world():
    world = EntityWorld()

    world.add_system(RenderSystem())
    world.add_manager(EntityManager())

    blue_crystal = EntityFactory.create_blue_crystal(world, (50, 50))
    world.add_entity(blue_crystal)

    return world


if __name__ == "__main__":

    consts = {
        "window" : {
            "width": 800,
            "height": 600,
            "vsync": True,
            "resizable": True
        }
    }

    initialize_system()
    world = create_game_world()

    cocos.director.director.init(**consts["window"])
    scene = cocos.scene.Scene()
    scene.add(GraphicsTestLayer(world), z=0)
    cocos.director.director.run(scene)
