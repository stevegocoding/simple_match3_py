import time
import cocos.layer
import cocos.scene
import cocos.batch
import cocos.sprite
from src.framework import component, utils


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
    def order_indxe(self):
        return self._order_index

    @property
    def is_hidden(self):
        return self._is_hidden


class SceneComponent(component.Component):
    def __init__(self):
        component.Component.__init__(self)
        self._cocos_node = cocos.cocosnode.CocosNode()

    @property
    def position(self):
        return self._cocos_node.position

    @position.setter
    def position(self, (x, y)):
        self._cocos_node.position = (x, y)


class SpriteRenderer(component.Component):

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

        scene_node = self.owner.get_component(SceneComponent)
        if self.owner is not None and scene_node is not None:
            self._position = scene_node.position

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
        print "Sprite Renderer attached! owner: %s, previous: %s" % (type(state_event_args.owner).__name__,
                                                                     type(state_event_args.previous_owner).__name__)
        #if state_event_args.owner is not None:
        #    state_event_args.owner.add(self.renderable_object)

    def on_renderer_detached(self, state_event_args):
        print "Sprite Renderer detached!"

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

