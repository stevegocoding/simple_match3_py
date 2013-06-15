__author__ = 'magkbdev'

import cocos.director
import cocos.layer
import cocos.scene
import cocos.batch
import cocos.sprite

import pyglet.gl as gl
import pyglet.resource

from simple_match3.resource import GameAssetArchiveLoader
from simple_match3.resource import ResourceManager
from simple_match3.entity import Aspect
from simple_match3.entity import EntitySystem
from simple_match3.world import EntityWorld
from simple_match3.managers import EntityManager
from simple_match3.utils import FPSSync

from entity_factory import PositionComponent
from entity_factory import SpriteRenderComponent


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

    def check_processing(self):
        return True

    def process_entities(self, entities):
        for entity in entities:
            self.render_entity(entity)


class GraphicsTestLayer(cocos.layer.Layer):

    def __init__(self, world):
        super(GraphicsTestLayer, self).__init__()

        self._world = world
        self._counter = 0

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def draw(self):

        self._counter += 1
        print "GraphicsTestLayer - draw() %d" % self._counter

        gl.glPushMatrix()

        self.transform()

        self._world.begin()
        self._world.process()
        self._world.end()

        gl.glPopMatrix()


class GameScene(cocos.scene.Scene):

    fps_sync = FPSSync(60)

    def __init__(self):
        cocos.scene.Scene.__init__(self)
        GameScene.fps_sync.start()
        self.schedule(self.update_tick_counter)

    def update_tick_counter(self, dt):
        print "dt: %f" % dt
        GameScene.fps_sync.update(dt)

    def visit(self):
        """
        ticks = GameScene.fps_sync.get_frame_count()

        if ticks > 0:
            process_count = 0
            while process_count < ticks:
                # cocos.scene.Scene.visit(self)
                process_count += 1
        """

        cocos.scene.Scene.visit(self)

    

    @staticmethod
    def frame_count():
        return GameScene.fps_sync.get_frame_count()

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
    scene = GameScene()
    #scene = cocos.scene.Scene()
    scene.add(GraphicsTestLayer(world), z=0)

    cocos.director.event_loop._polling = True

    cocos.director.director.run(scene)
