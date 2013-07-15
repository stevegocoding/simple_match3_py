
from simple_match3.resource import GameAssetArchiveLoader
from simple_match3.entity import Aspect
from simple_match3.entity import EntitySystem
from simple_match3.managers import EntityManager
from simple_match3.utils import State

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
                                                                  BoardRenderComponent,
                                                                  GemsSpawnComponent]))

    def render(self):
        if len(self._active_entities) == 0:
            return
        self.render_board(self._active_entities[0])

    def render_board(self, entity):
        render_component = entity.get_component(BoardRenderComponent)
        items_component = entity.get_component(BoardItemsComponent)

        render_component.update_render_position(items_component)
        render_component.render()

    def spawn_gem(self, pos):
        if len(self._active_entities) == 0:
            return
        spawner_entity = self._active_entities[0]
        spawn_component = spawner_entity.get_component(GemsSpawnComponent)
        spawn_component.spawn_gem(app_root.world, pos)

    @property
    def board_width(self):
        items_component = self._active_entities[0].get_component(BoardItemsComponent)
        return items_component.board_width

    @property
    def board_height(self):
        items_component = self._active_entities[0].get_component(BoardItemsComponent)
        return items_component.board_height


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


class GameStateSystem(EntitySystem):

    init_game_state = "init_game"
    fill_board_state = "fill_board"

    # State data keys
    total_gems_key = "total_gems"
    spawn_gems_key = "spawn_gems"
    last_spawn_tick_key = "last_spawn_tick"

    def __init__(self):
        super(GameStateSystem, self).__init__(Aspect.create_aspect_for_all([]))
        self._state = State()

        fill_board_state = State()
        fill_board_state.assign({"id": self.fill_board_state,
                                 "enter_func": self._on_fill_board_enter,
                                 "process_func": self._on_fill_board_process,
                                 "exit_func": self._on_fill_board_exit})
        self.state.add_state(fill_board_state)

    def _on_fill_board_enter(self, state):
        pass

    def _on_fill_board_process(self, state):

        if state.tick - state.data[self.last_spawn_tick_key] >= 5:
            total_gems = state.data[self.total_gems_key]
            spawn_gems = state.data[self.spawn_gems_key]

            board_render_system = app_root.world.get_system_by_type(BoardRenderSystem)

            if spawn_gems < total_gems:
                for i in range(board_render_system.board_width):
                    pos = i, board_render_system.board_height-1
                    board_render_system.spawn_gem(pos)
                    state.data[self.spawn_gems_key] += 1

                state.data[self.last_spawn_tick_key] = state.tick

    def _on_fill_board_exit(self, state):
        pass

    def process(self):
        self._state.process()

    @property
    def state(self):
        return self._state


def init_game():
    asset_loader = GameAssetArchiveLoader()
    asset_loader.level("test_level")

    world = app_root.world
    world.add_system(BoardRenderSystem(), layer_name="BOARD_LAYER")
    world.add_system(GemsRenderSystem(), layer_name="PIECE_LAYER")
    world.add_system(GameStateSystem(), layer_name="BACKGROUND_LAYER")

    world.add_manager(EntityManager())

    board_entity = EntityFactory.create_game_board(world, "board_blocks_test_hole.json", (200, 70))
    world.add_entity(board_entity)

    #gem_entity = EntityFactory.create_gem(world, board_entity, "pink_hex", (3, 9))
    #world.add_entity(gem_entity)

    world.get_system_by_type(GameStateSystem).state.set_state(GameStateSystem.fill_board_state,{"total_gems": 100,"spawn_gems": 0,"last_spawn_tick": 0})


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