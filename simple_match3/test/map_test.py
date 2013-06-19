__author__ = 'magkbdev'

import cocos.director
import cocos.layer
import cocos.scene
import cocos.batch
import cocos.sprite

import pyglet.gl as gl
import pyglet.resource

from simple_match3.resource import GameAssetArchiveLoader
from simple_match3.entity import Aspect
from simple_match3.entity import EntitySystem
from simple_match3.world import EntityWorld
from simple_match3.managers import EntityManager
from simple_match3.utils import FPSSync

from entity_factory import BoardTilePositionComponent
from entity_factory import BoardRenderComponent
from entity_factory import BackgroundRenderComponent


class BoardRenderSystem(EntitySystem):

    def __init__(self):
        EntitySystem.__init__(self, Aspect.create_aspect_for_all([BoardTilePositionComponent,
                                                                  BoardRenderComponent]))

    def render(self):
        for entity in self._active_entities:
            self.render_entity(entity)

    def render_entity(self, entity):
        render_component = entity.get_component(BoardRenderComponent)
        #position_component = entity.get_component(BoardTilePositionComponent)

        render_component.render()


class BackgroundRenderSystem(EntitySystem):

    def __init__(self):
        EntitySystem.__init__(self, Aspect.create_aspect_for_all([BackgroundRenderComponent]))

    def render(self):
        for entity in self._active_entities:
            self.render_entity(entity)

    def render_entity(self, entity):
        render_component = entity.get_component(BackgroundRenderComponent)
        render_component.render()


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
        self._world.render()
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
    pyglet.resource.path = ["assets", "assets/gfx", "assets/sound", "assets/map"]
    pyglet.resource.reindex()

    asset_loader = GameAssetArchiveLoader()
    asset_loader.level("test_level")


def create_game_world():
    world = EntityWorld()

    world.add_system(BackgroundRenderSystem())
    world.add_manager(EntityManager())

    bg_entity = EntityFactory.create_background(world, "background.json")
    world.add_entity(bg_entity)

    return world


if __name__ == "__main__":

    consts = {
        "window" : {
            "width": 1024,
            "height": 768,
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