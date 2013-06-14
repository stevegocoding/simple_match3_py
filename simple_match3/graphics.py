import time
import cocos.layer
import cocos.scene
import cocos.batch
import cocos.sprite

import utils

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

