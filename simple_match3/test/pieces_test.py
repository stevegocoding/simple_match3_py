
from simple_match3.resource import GameAssetArchiveLoader
from simple_match3.entity import Aspect
from simple_match3.entity import EntitySystem
from simple_match3.managers import EntityManager

from entity_factory import BoardItemsComponent
from entity_factory import BoardTilePositionComponent
from entity_factory import BoardRenderComponent
from entity_factory import GemsRenderComponent
from entity_factory import GemsPositionComponent
from entity_factory import GemsSpawnComponent
from entity_factory import PhysicsComponent
from entity_factory import EntityFactory

from simple_match3.game import app_root


class BoardRenderSystem(EntitySystem):

    def __init__(self):
        EntitySystem.__init__(self, Aspect.create_aspect_for_all([BoardTilePositionComponent,
                                                                  BoardRenderComponent]))

    def render(self):
        self.render_board(self._active_entities[0])

    def render_board(self, entity):
        render_component = entity.get_component(BoardRenderComponent)
        position_component = entity.get_component(BoardTilePositionComponent)

        render_component.update_render_position(position_component)
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
        EntitySystem.__init__(self, Aspect.create_aspect_for_all([GemsRenderComponent]))

    def render(self):
        for entity in self._active_entities:
            self.render_entity(entity)

    def render_entity(self, entity):
        render_component = entity.get_component(GemsRenderComponent)
        pos_component = entity.get_component(GemsPositionComponent)

        render_pos = pos_component.get_render_position()

        render_component.render_position = render_pos
        render_component.render()


class GemsSpawnSystem(EntitySystem):

    def __init__(self):
        super(GemsSpawnSystem, self).__init__(
            Aspect.create_aspect_for_all([GemsSpawnComponent]))

    def on_event(self, event_args):
        if event_args.event_type == "spawn_event":
            spawn_pipes = event_args.pipes
            for i in spawn_pipes:
                pipe = self._get_spawn_pipe(i)
                self._spawn_gem(pipe)

    def _spawn_gem(self, spawn_pipe):
        spawn_pos = self._get_spawn_pos(spawn_pipe)
        gem_type = self._get_spawn_type(spawn_pipe)
        EntityFactory.create_gem(app_root.world, gem_type, spawn_pos)

    def _get_spawn_pipe(self, idx):
        return self._active_entities[idx]

    def _get_spawn_pos(self, pipe):
        spawn_component = pipe.get_component(GemsSpawnComponent)
        return spawn_component.spawn_pos

    def _get_spawn_type(self, pipe):
        spawn_component = pipe.get_component(GemsSpawnComponent)
        return spawn_component.next_gem_type


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

    gem_entity = EntityFactory.create_gem(world, board_entity, "pink_hex", (2, 1))
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