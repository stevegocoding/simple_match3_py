
from simple_match3.resource import GameAssetArchiveLoader
from simple_match3.entity import Aspect
from simple_match3.entity import EntitySystem
from simple_match3.managers import EntityManager

from entity_factory import BoardItemsComponent
from entity_factory import BoardRenderComponent
from entity_factory import GemsRenderComponent
from entity_factory import GemsItemComponent
from entity_factory import GemsSpawnComponent
from entity_factory import EntityFactory

from simple_match3.game import app_root


class BoardRenderSystem(EntitySystem):

    def __init__(self):
        EntitySystem.__init__(self, Aspect.create_aspect_for_all([BoardItemsComponent,
                                                                  BoardRenderComponent]))

    def render(self):
        self.render_board(self._active_entities[0])

    def render_board(self, entity):
        render_component = entity.get_component(BoardRenderComponent)
        items_component = entity.get_component(BoardItemsComponent)

        render_component.update_render_position(items_component)
        render_component.render()


class BoardItemsSystem(EntitySystem):

    def __init__(self):
        EntitySystem.__init__(self, Aspect.create_aspect_for_all([BoardItemsComponent]))
        self._board_entity = None

    def is_cell_accessible(self, row, col):
        items_component = self._board_entity.get_component(BoardItemsComponent)
        return items_component.is_cell_accessible(row, col)


class GemsRenderSystem(EntitySystem):

    def __init__(self):
        EntitySystem.__init__(self, Aspect.create_aspect_for_all([GemsRenderComponent,
                                                                  GemsItemComponent]))

    def render(self):
        for entity in self._active_entities:
            self.render_entity(entity)

    def render_entity(self, entity):
        render_component = entity.get_component(GemsRenderComponent)
        pos_component = entity.get_component(GemsItemComponent)

        render_component.render_position = pos_component.render_position
        render_component.render()

    def process(self):
        for entity in self._active_entities:
            self.process_entity(entity)

    def process_entity(self, entity):
        item_component = entity.get_component(GemsItemComponent)
        item_component.process()


class GemsSpawnSystem(EntitySystem):

    def __init__(self):
        super(GemsSpawnSystem, self).__init__(
            Aspect.create_aspect_for_all([GemsSpawnComponent]))

    def on_event(self, event_args):
        if event_args.event_type == "spawn_event":
            spawn_pipes = event_args.pipes
            for i in spawn_pipes:
                pipe = self._get_spawn_pipe(i)
                pipe.spawn_gem(app_root.world)


class GemsPhysicsSystem(EntitySystem):

    def __init__(self):
        super(GemsPhysicsSystem, self).__init__(Aspect.create_aspect_for_all([GemsRenderComponent,
                                                                              PhysicsComponent]))

    def process_entities(self, entities):
        for entity in entities:
            physics_component = entity.get_component(PhysicsComponent)
            physics_component.update_gem_pos()


def init_game():
    asset_loader = GameAssetArchiveLoader()
    asset_loader.level("test_level")

    world = app_root.world
    world.add_system(BoardRenderSystem(), layer_name="BOARD_LAYER")
    world.add_system(GemsRenderSystem(), layer_name="PIECE_LAYER")
    world.add_manager(EntityManager())

    board_entity = EntityFactory.create_game_board(world, "board_blocks_test_hole.json", (200, 70))
    world.add_entity(board_entity)

    gem_entity = EntityFactory.create_gem(world, board_entity, "pink_hex", (3, 9))
    world.add_entity(gem_entity)

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