import time
import cocos.layer
import cocos.scene
import cocos.batch
import cocos.sprite

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

