__author__ = 'magkbdev'

import time
import pyglet.resource
import cocos.scene
import cocos.sprite

import entity
import component
import utils


class GameScene(cocos.scene.Scene):

    fps_sync = utils.FPSSync(30)

    def __init__(self):
        cocos.scene.Scene.__init__(self)
        GameScene.fps_sync.start()
        self.schedule(self.update_tick_counter)

        self.game_entities = []

    def add_game_entity(self, entity):
        self.game_entities.append(entity)

    def remove_game_entity(self, entity):
        pass

    def update_tick_counter(self, dt):
        print "dt: %f" % dt
        GameScene.fps_sync.update(dt)

    def process_scene(self):
        ticks = GameScene.fps_sync.get_frame_count()
        print "real_time: %f" % GameScene.fps_sync.real_time
        print "time_stamp: %f" % GameScene.fps_sync.time_stamp
        print "ticks1 : %f" % ticks
        if ticks > 0:
            process_count = 0
            print "ticks2 : %f" % ticks
            while process_count < ticks:
                print "GameScene process()"
                process_count += 1
                for entity in self.game_entities:
                    entity.process()

    def visit(self):
        print "GameScene visit()"

        self.process_scene()

        print "GameScene render()"

        cocos.scene.Scene.visit(self)


        print "======================"

    def draw(self, *args, **kwargs):
        time.sleep(2)

    @staticmethod
    def frame_count():
        return GameScene.fps_sync.get_frame_count()


class Cell(object):

    def __init__(self, board, cell_x, cell_y, type):
        self._board = board
        self._cell_x = cell_x
        self._cell_y = cell_y
        self._type = type
        self._piece = None


class SpriteRenderComponent(component.RenderComponent):

    def __init__(self):
        component.Component.__init__(self)
        self._current_state = "default"
        self._frame_index = 0
        self._max_frames = 0
        self._sprites = []
        self._layers = []
        self._layers_render = []
        self._loop = True
        self._animation_percent = 0
        self._position = (0, 0)

        self.on_component_attached = self.on_renderer_attached
        self.on_component_detached = self.on_renderer_detached

    def create_layer(self, resource, order_index):
        layer = graphics.SpriteSheetLayer(self, resource, order_index)
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

    def on_renderer_attached(self, state_event_args):
        print "Sprite Renderer attached! owner: %s, previous: %s" % \
              (type(state_event_args.owner).__name__,
               type(state_event_args.previous_owner).__name__)

    def on_renderer_detached(self, state_event_args):
        print "Sprite Renderer detached!"

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, val):
        self._position = val

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


class BoardPositionComponent(component.Component):
    """
    Contains and manages all the cells in this board
    """

    def __init__(self):
        component.Component.__init__(self)
        self._cells_list = []
        self._state = utils.State()


class BoardGenerateComponent(component.Component):
    """
    Responsible generating/updating the pieces on the board
    """

    def __init__(self):
        pass


class BoardRenderComponent(component.RenderComponent):

    def __init__(self):
        component.Component.__init__(self)
        self._alpha = 0.25
        self._image = pyglet.resouce.image("../assets/board_base.png")
        self._sprite = cocos.sprite.Sprite(self._image)

    def render_frame(self):
        self._sprite.draw()

    def update_frame(self, animation_ticks=1):
        pass


class PieceComponent(component.Component):

    """
    The piece represents all the objects that is located in the board and
    respecting the coordinate system defined by the board and cells. Also
    they can be eliminated when there is a match-3.
    """

    def __init__(self, type):
        component.Component.__init__(self)
        self._type = type
        self._state = utils.State()

    def draw(self):
        pass


# Testing
if __name__ == "__main__":

    import cocos.director
    import cocos.layer

    import game

    consts = {
        "window" : {
            "width": 800,
            "height": 600,
            "vsync": True,
            "resizable": True
        }
    }

    cocos.director.director.init(**consts["window"])
    scene = graphics.GameScene()
    base_layer = cocos.layer.Layer()

    components = [game.BoardRenderComponent]
    entity.Entity.define("TestBoardEntityDefine", components)
    board_entity = entity.Entity.create_from_def("TestBoardEntityDefine", "board_entity")
    base_layer.add(board_entity)

    scene.add(base_layer, z=-1)
    scene.add_game_entity()

