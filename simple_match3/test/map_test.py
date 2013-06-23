from simple_match3.resource import GameAssetArchiveLoader
from simple_match3.entity import Aspect
from simple_match3.entity import EntitySystem
from simple_match3.managers import EntityManager

from entity_factory import BoardTilePositionComponent
from entity_factory import BoardRenderComponent
from entity_factory import BackgroundRenderComponent
from entity_factory import EntityFactory


class BoardRenderSystem(EntitySystem):

    def __init__(self):
        EntitySystem.__init__(self, Aspect.create_aspect_for_all([BoardTilePositionComponent,
                                                                  BoardRenderComponent]))

    def render(self):
        for entity in self._active_entities:
            self.render_entity(entity)

    def render_entity(self, entity):
        render_component = entity.get_component(BoardRenderComponent)
        position_component = entity.get_component(BoardTilePositionComponent)

        render_component.update_render_position(position_component)
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


from simple_match3.game import app_root


def init_game():
    asset_loader = GameAssetArchiveLoader()
    asset_loader.level("test_level")

    world = app_root.world
    world.add_system(BackgroundRenderSystem())
    world.add_system(BoardRenderSystem(), layer_name="BOARD_LAYER")
    world.add_manager(EntityManager())

    bg_entity = EntityFactory.create_background(world, "background.json")
    #world.add_entity(bg_entity)

    board_entity = EntityFactory.create_game_board(world, "board_blocks.json", (200, 70))
    world.add_entity(board_entity)

if __name__ == "__main__":

    app_config = {
        "window": {
            "width": 1024,
            "height": 768,
            "vsync": True,
            "resizable": True
        },
        "resource": {
            "resource_path": ["assets", "assets/gfx", "assets/sound", "assets/map"]
        }
    }

    app_root.init(**app_config)

    init_game()

    app_root.run()