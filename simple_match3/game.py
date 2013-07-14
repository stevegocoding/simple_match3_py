__author__ = 'magkbdev'

import cocos.director as director
import cocos.scene as scene
import cocos.layer as layer
import cocos.cocosnode as cocosnode

import pyglet.app
import pyglet.resource
import pyglet.gl as gl

from world import EntityWorld
from utils import FPSSync


class EntitySystemNode(cocosnode.CocosNode):

    def __init__(self, entity_system):
        super(EntitySystemNode, self).__init__()
        self._entity_system = entity_system

    def visit(self):
        if not self.visible:
            return

        self._entity_system.process()
        self._entity_system.render()

    @property
    def z_index(self):
        return 0

    @property
    def name(self):
        return "default"


class GameScene(scene.Scene):

    fps_sync = FPSSync(60)

    def __init__(self):
        super(GameScene, self).__init__()
        GameScene.fps_sync.start()
        #self.schedule(self.update_tick_counter)

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

        scene.Scene.visit(self)

    @staticmethod
    def frame_count():
        return GameScene.fps_sync.get_frame_count()


class CocosEntityWorld(EntityWorld):

    _layers_def = {
        "BACKGROUND_LAYER": 0,
        "BOARD_LAYER": 1,
        "CELL_ELEM_LAYER": 2,
        "PIECE_LAYER": 3
    }

    def __init__(self):

        super(CocosEntityWorld, self).__init__()

        # The root node of all the entities in the world
        self._scene_node = GameScene()
        #self._scene_node = scene.Scene()
        self._init_layers()

    def _init_layers(self):
        for name, index in self._layers_def.items():
            l = layer.Layer()
            self._scene_node.add(l, z=index, name=name)

    def add_system(self, system, layer_name="BACKGROUND_LAYER"):
        super(CocosEntityWorld, self).add_system(system)

        system_node = EntitySystemNode(system)
        layer = self._scene_node.get(layer_name)
        layer.add(system_node, z=system_node.z_index, name=system_node.name)

    def run_world_frame(self):
        self._scene_node.visit()

    @property
    def scene(self):
        return self._scene_node


class Root(object):

    def __init__(self):
        self._world = None

    def init(self, *args, **kwargs):
        director.director.init(*args, **kwargs["window"])
        self._create_world()
        self._init_system(**kwargs["resource"])

        director.director.window.remove_handlers(director.director.on_draw)
        director.director.window.push_handlers(self.on_draw)
        director.director.window.on_draw = self.dummy_on_draw

        pyglet.clock.schedule_interval(self.invalide_window, 1/60.0)

    def _create_world(self):
        self._world = CocosEntityWorld()

    def _init_system(self, **kwargs):
        for keyword, value in kwargs.items():
            if keyword == "resource_path":
                pyglet.resource.path = value
                pyglet.resource.reindex()

    def run(self):
        director.event_loop.run()
        #director.director.run(self._world.scene)

    @property
    def world(self):
        return self._world

    def dummy_on_draw(self):
        pass

    def invalide_window(self, dt):
        director.director.window.invalid = True

    def on_draw(self):
        """Handles the event 'on_draw' from the pyglet.window.Window

            Realizes switch to other scene and app termination if needed
            Clears the window area
            The windows is painted as:

                - Render the current scene by calling it's visit method
                - Eventualy draw the fps metter
                - Eventually draw the interpreter

            When the window is minimized any pending switch to scene will be
            delayed to the next de-minimizing time.
        """

        print "on_draw()"

        # typically True when window minimized
        if ((director.director.window.width == 0 or director.director.window.height == 0) and
                not director.director.terminate_app):
            # if surface area is zero, we don't need to draw; also
            # we dont't want to allow scene changes in this situation: usually
            # on_enter does some scaling, which would lead to division by zero
            return

        # handle scene changes and app termination
        if director.director.terminate_app:
            director.director.next_scene = None

        if director.director.next_scene is not None or director.director.terminate_app:
            director.director._set_scene(director.director.next_scene)

        if director.director.terminate_app:
            pyglet.app.exit()
            return

        # Start the render loop
        director.director.window.clear()

        gl.glPushMatrix()

        self.render_frame()

        gl.glPopMatrix()

    def render_frame(self):
        self._world.begin()
        self._world.run_world_frame()
        self._world.end()


# Root Singleton
# Don't use Root(), only use this singleton.
app_root = Root()