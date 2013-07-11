__author__ = 'magkbdev'

import pyglet.gl as gl
import pyglet.graphics

from pyglet.sprite import Sprite
from pyglet.graphics import Batch
from pyglet.image import Texture

from gletools import (ShaderProgram, VertexShader, FragmentShader, Framebuffer, Sampler2D)

from gl_utils import TextureContext

from simple_match3.managers import EntityManager
from simple_match3.entity import EntityRecord
from simple_match3.component import Component
from simple_match3.resource import ResourceManagerSingleton
from simple_match3.utils import State

import random


class SpriteSheetLayer(object):

    def __init__(self, renderer, resource, order_idx):
        self._name = "default_layer"
        self._renderer = renderer
        self._sprite_sheet = resource
        self._order_index = order_idx
        self._is_hidden = False

        image = self.get_frame_image(self._renderer.current_state, self._renderer.current_frame)
        self._sprite = Sprite(image)

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

    def draw(self):
        image = self.get_frame_image(self._renderer.current_state, self._renderer.current_frame)
        pos = self._renderer.position

        if image is not None:
            self._sprite._set_image(image)
            self._sprite.position = pos
            self._sprite.draw()

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


class SpriteRenderComponent(Component):

    def __init__(self, spritesheet_resources=None):
        Component.__init__(self)

        self._current_state = "default"
        self._frame_index = 0
        self._max_frames = 0
        self._layers = []
        self._layers_render = []
        self._loop = True
        self._animation_percent = 0
        self._position = (0, 0)

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
                self._layers_render.append(layer)

    def render_frame(self):
        for layer in self._layers_render:
            layer.draw()

        # clear the list of the layers to render
        self._layers_render = []

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

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value


class PositionComponent(Component):

    def __init__(self):
        Component.__init__(self)

    def get_position(self):
        return 100, 100


class BoardTilePositionComponent(Component):

    def __init__(self, origin_pos, cell_width, cell_height, num_cols, num_rows):
        Component.__init__(self)

        self._origin_x = origin_pos[0]
        self._origin_y = origin_pos[1]
        self._num_cols = num_cols
        self._num_rows = num_rows
        self._cell_width = cell_width
        self._cell_height = cell_height

    def get_render_position(self, x, y):
        pos_x = 0
        pos_y = 0
        if x < self._num_cols and y < self._num_rows:
            pos_x = self._origin_x + x * self._cell_width
            pos_y = self._origin_y + y * self._cell_height

        return pos_x, pos_y

    @property
    def origin_position(self):
        return self._origin_x, self._origin_y

    @origin_position.setter
    def origin_position(self, val):
        self._origin_x = val[0]
        self._origin_y = val[1]

    @property
    def cell_width(self):
        return self._cell_width

    @property
    def cell_height(self):
        return self._cell_height

    @property
    def num_cols(self):
        return self._num_cols

    @property
    def num_rows(self):
        return self._num_rows


class BoardCell(object):

    def __init__(self, row, col, accessible):
        self._row = row
        self._col = col
        self._accessible = accessible
        if accessible:
            self._items = list()
        else:
            self._items = None

    def clear_items(self):
        if self._items:
            del self._items[:]

    def add_item(self, item):
        if self._items:
            self._items.append(item)

    @property
    def accessible(self):
        return self._accessible


class BoardItemsComponent(Component):
    """
    Manages the logic items in the board, such as some blockers...
    """

    tileset_name = "gems2_small_alpha"

    def __init__(self, board_res):
        super(BoardItemsComponent, self).__init__()

        self._cell_width = board_res.tile_width
        self._cell_height = board_res.tile_height
        self._board_width = board_res.board_width
        self._board_height = board_res.board_height

        self._board_cells = None
        self._init_cells(board_res)

    def _init_cells(self, board_res):
        self._board_cells = [[]]
        tiles = None
        for layer in board_res.layers:
            if layer.type == "tilelayer":
                tiles = list(layer.tiles)
                break

        properties = board_res.get_tileset_properties(self.tileset_name)
        inaccessible_tile = properties["inaccessible_tile"]

        if len(tiles) == board_res.board_width * board_res.board_height:
            for i in range(board_res.board_height):
                self._board_cells.append(list())
                for j in range(board_res.board_width):
                    accessible = tiles[i*board_res.board_width + j] == inaccessible_tile
                    self._board_cells[i].append(BoardCell(i, j, accessible))

    def get_cell(self, row, col):
        return self._board_cells[row][col]

    def get_cell_by_render_pos(self, pos, board_render_pos):
        local = self._render_pos_to_local(pos, board_render_pos)
        col = local[0] / self._cell_width
        row = local[1] / self._cell_height

        return self.get_cell(row, col)

    def is_cell_accessible(self, row, col):
        cell = self.get_cell(row, col)
        return cell.accessible

    def _render_pos_to_local(self, pos, board_render_pos):
        return pos - board_render_pos


class BoardRenderComponent(Component):

    _simple_tex_vs = VertexShader(
        """
        varying vec2 texcoords;
        void main()
        {
            gl_Position = ftransform();
            texcoords = gl_MultiTexCoord0.st;
        }
        """
    )

    _simple_tex_fs = FragmentShader(
        """
        varying vec2 texcoords;
        uniform sampler2D in_tex;
        void main()
        {
            vec4 tex_color = texture2D(in_tex, texcoords);
            gl_FragColor = tex_color;
        }
        """
    )

    _blend_fs = FragmentShader(
        """
        varying vec2 texcoords;
        uniform sampler2D bg_tex;
        uniform sampler2D tiles_tex;
        void main()
        {
            vec4 bg_color = texture2D(bg_tex, texcoords);
            vec4 tile_color = texture2D(tiles_tex, texcoords);
            vec4 result = vec4(0.0, 0.0, 0.0, 0.0);
            vec3 white = vec3(1.0, 1.0, 1.0);
            //result.xyz = bg_color.xyz * 0.6 + tile_color.xyz * 0.4;
            //result.xyz = bg_color.xyz * (white - tile_color.xyz) + tile_color.xyz;
            result.xyz = bg_color.xyz * (1.0 - tile_color.w) + tile_color.xyz * tile_color.w;
            gl_FragColor.xyz = result.xyz;
            gl_FragColor.w = 1;
        }
        """
    )

    _bg_vertex_list = None
    _tiles_vertex_list = None

    _simple_tex_shader = None
    _blend_shader = None

    _bg_tex = None
    _bg_tex_context = None
    _bg_render_tex = None
    _bg_render_tex_context = None
    _bg_frame_buffer = Framebuffer()

    _tiles_render_tex = None
    _tiles_render_tex_context = None
    _tiles_frame_buffer = Framebuffer()

    def __init__(self, board_layout_res):
        Component.__init__(self)

        self._board_res = board_layout_res
        self._tiles_sprites = []
        self._tiles_batch = None

        self._bg_tex = self._board_res.get_image_layer_texture("background")

        self._board_position = 0, 0
        self._x = 0
        self._y = 0

        self._bg_rtt_flag = True
        self._tiles_rtt_flag = True

        self.create_tiles_sprite_batch()
        self.create_gpu_resources()

    def create_tiles_sprite_batch(self):
        self._tiles_batch = Batch()

        for layer in self._board_res.layers:
            if layer.type == "tilelayer" and layer.name != "items_layer":
                for tile in layer.tiles:
                    if tile == 17:
                        continue
                    tex = self._board_res.get_tile_image(tile)
                    sprite = Sprite(tex)
                    self._tiles_sprites.append(sprite)

    def create_gpu_resources(self):
        # Create the vertex list for the background quad
        self._bg_vertex_list = pyglet.graphics.vertex_list(4,
                                                           'v2i/%s' % "dynamic",
                                                           'c4b', ('t3f', self._bg_tex.tex_coords))

        # Setup the texture contexts
        self._bg_tex_context = TextureContext(self._bg_tex)
        self._bg_render_tex = Texture.create(self._bg_tex.width, self._bg_tex.height, gl.GL_RGBA)
        self._bg_render_tex_context = TextureContext(self._bg_render_tex)

        # Update the vertices
        self._update_vertices_position(self._bg_tex, self._bg_vertex_list)

        self._tiles_render_tex = Texture.create(self._bg_tex.width, self._bg_tex.height, gl.GL_RGBA)
        self._tiles_render_tex_context = TextureContext(self._tiles_render_tex, unit=gl.GL_TEXTURE1)

        # Create the vertex list
        self._tiles_vertex_list = pyglet.graphics.vertex_list(4,
                                                              'v2i/%s' % "dynamic",
                                                              'c4b', ('t3f', self._tiles_render_tex.tex_coords))
        self._update_vertices_position(self._tiles_render_tex, self._tiles_vertex_list)

        # Setup the frame buffers
        self._bg_frame_buffer.textures = [self._bg_render_tex_context]
        self._tiles_frame_buffer.textures = [self._tiles_render_tex_context]

        # Setup the shader program
        self._simple_tex_shader = ShaderProgram(
            self._simple_tex_vs,
            self._simple_tex_fs
        )
        self._simple_tex_shader.vars.in_tex = Sampler2D(gl.GL_TEXTURE0)
        self._blend_shader = ShaderProgram(
            self._simple_tex_vs,
            self._blend_fs
        )
        self._blend_shader.vars.bg_tex = Sampler2D(gl.GL_TEXTURE0)
        self._blend_shader.vars.tiles_tex = Sampler2D(gl.GL_TEXTURE1)

    def _update_vertices_position(self, tex, vertex_list):
        x1 = int(self._x - tex.anchor_x)
        y1 = int(self._y - tex.anchor_y)
        x2 = x1 + tex.width
        y2 = y1 + tex.height
        vertex_list.vertices[:] = [x1, y1, x2, y1, x2, y2, x1, y2]

    def render(self):

        #if self._bg_rtt_flag:
        self._render_bg_to_texture()

        #self._test_bg_render()

        #if self._tiles_rtt_flag:
        self._render_tiles_to_one_texture()

        #self._test_sprites_render2()

        self._render_tiles_with_bg()

    def update_render_position(self, position_component):
        if position_component:
            sprite_idx = 0
            tile_idx = 0
            for layer in self._board_res.layers:
                if layer.name == "items_layer":
                    break

                for tile in layer.tiles:
                    if tile == 17:
                        tile_idx += 1
                        continue
                    if sprite_idx >= len(self._tiles_sprites):
                        break
                    x, y = self._get_tile_xy(tile_idx, layer.width, layer.height)
                    sprite = self._tiles_sprites[sprite_idx]
                    sprite.position = position_component.get_render_position(x, y)
                    sprite_idx += 1
                    tile_idx += 1
        else:
            raise Exception("There is no BoardTilePositionComponent attached yet")

    def _get_tile_xy(self, tile_idx, num_tiles_x, num_tiles_y):
        if num_tiles_x != 0 and num_tiles_y != 0:
            tile_y = tile_idx / num_tiles_x
            tile_x = tile_idx - tile_y * num_tiles_x
            return tile_x, tile_y
        return -1, -1

    def _render_bg_to_texture(self):
        self._bg_frame_buffer.drawto = [gl.GL_COLOR_ATTACHMENT0_EXT]
        with self._bg_frame_buffer, self._bg_tex_context, self._simple_tex_shader:
            self._bg_vertex_list.draw(gl.GL_QUADS)
            self._bg_rtt_flag = False

    def _render_tiles_to_one_texture(self):
        self._tiles_frame_buffer.drawto = [gl.GL_COLOR_ATTACHMENT0_EXT]
        with self._tiles_frame_buffer, self._simple_tex_shader:
            for sprite in self._tiles_sprites:
                sprite.draw()

            self._tiles_rtt_flag = False

    def _test_bg_render(self):
        with self._bg_render_tex_context, self._simple_tex_shader:
            self._bg_vertex_list.draw(gl.GL_QUADS)

    def _test_sprites_render(self):
        with self._tiles_render_tex_context, self._simple_tex_shader:
            self._tiles_vertex_list.draw(gl.GL_QUADS)

    def _test_sprites_render2(self):
        for sprite in self._tiles_sprites:
            sprite.draw()

    def _render_tiles_with_bg(self):
        with self._bg_render_tex_context, self._tiles_render_tex_context, self._blend_shader:
            self._tiles_vertex_list.draw(gl.GL_QUADS)


class BackgroundRenderComponent(Component):

    _vertex_list = None
    _bg_render_vs = VertexShader(
        """
        varying vec2 texcoords;
        void main()
        {
            gl_Position = ftransform();
            texcoords = gl_MultiTexCoord0.st;
        }
        """
    )

    _bg_render_fs = FragmentShader(
        """
        varying vec2 texcoords;
        uniform sampler2D bg_tex;

        void main()
        {
            vec4 tex_color = vec4(0.0, 0.0, 0.0, 0.0);
            tex_color = texture2D(bg_tex, texcoords);
            gl_FragColor = tex_color;
            gl_FragColor.w = 1;
        }
        """
    )

    _bg_shader = None
    _tex_context = None
    _usage = "dynamic"

    def __init__(self, bg_res, x, y):
        Component.__init__(self)

        self._bg_res = bg_res
        self._bg_tex = bg_res.texture

        self._x = x
        self._y = y

        self._setup_geometry()
        self._setup_shader_program()
        self._setup_texture_context(self._bg_tex)

    def __del__(self):
        if self._vertex_list is not None:
            self._vertex_list.delete()

    def _setup_geometry(self):
        self._vertex_list = pyglet.graphics.vertex_list(4,
                                                        'v2i/%s' % self._usage,
                                                        'c4b', ('t3f', self._bg_tex.tex_coords))
        self._update_position()

    def _update_position(self):
        img = self._bg_tex
        x1 = int(self._x - img.anchor_x)
        y1 = int(self._y - img.anchor_y)
        x2 = x1 + img.width
        y2 = y1 + img.height
        self._vertex_list.vertices[:] = [x1, y1, x2, y1, x2, y2, x1, y2]

    def _setup_texture_context(self, pyglet_tex):
        self._tex_context = TextureContext(pyglet_tex)

    def _setup_shader_program(self):
        self._bg_shader = ShaderProgram(
            self._bg_render_vs,
            self._bg_render_fs,
        )

        self._bg_shader.vars.bg_tex = Sampler2D(gl.GL_TEXTURE0)

    def render(self):
        with self._tex_context, self._bg_shader:
            self._vertex_list.draw(gl.GL_QUADS)


class GemsRenderComponent(Component):

    def __init__(self, sprite_sheet_res, type):
        super(GemsRenderComponent, self).__init__()

        self._type = type

        img = sprite_sheet_res.get_frame_img(type, 0)

        self._render_position = (0, 0)

        self._sprite = Sprite(img)

        self._state = State()

    def render(self):
        self._sprite.position = self._render_position
        self._sprite.draw()

    @property
    def render_position(self):
        return self._sprite.position

    @render_position.setter
    def render_position(self, pos):
        self._render_position = pos


class GemsSpawnComponent(Component):

    _gems_type = ["purple_quad",
                  "silver_triangle,"
                  "black_quad",
                  "green_hex,"
                  "purple_orb",
                  "green_orb"]

    def __init__(self, spawn_pos):
        super(GemsSpawnComponent, self).__init__()
        self._spawn_pos = spawn_pos
        self._num_gems_type = len(self._gems_type)

    def _generate_new_gem_idx(self):
        return random.randint(1, self._num_gems_type)

    @property
    def spawn_pos(self):
        return self._spawn_pos

    @property
    def next_gem_type(self):
        return self._generate_new_gem_idx()


class PhysicsComponent(Component):

    def __init__(self, pos):
        self._current_pos = pos
        self._current_cell = None
        self._collision_obj = None

        self._state = State()

        self._state.add_state(State().assign({"id": "falling_state",
                                              "enter_func": self._on_falling_enter,
                                              "process_func": self._on_falling_process,
                                              "exit_func": self._on_falling_exit}))

    def check_collision_cell(self, collision_obj):
        return False

    def update_collision_obj(self, render_pos, cell):
        pass

    @property
    def collision_obj(self):
        return self._collision_obj


class EntityFactory(object):
    def __init__(self):
        pass

    @staticmethod
    def create_blue_crystal(world, pos):
        entity = EntityRecord(world, world.get_manager_by_type(EntityManager).generate_id())

        pos_component = PositionComponent()
        entity.attach_component(pos_component)

        sprite_component = SpriteRenderComponent()
        sprite_resource = ResourceManagerSingleton.instance().find_resource("rotating_crystals")

        sprite_component.current_state = "crystal_blue"
        sprite_component.create_layer(sprite_resource, 0)
        entity.attach_component(sprite_component)

        return entity

    @staticmethod
    def create_background(world, background_res_name):
        entity = EntityRecord(world, world.get_manager_by_type(EntityManager).generate_id())

        bg_res = ResourceManagerSingleton.instance().find_resource(background_res_name)
        render_component = BackgroundRenderComponent(bg_res, 0, 0)
        entity.attach_component(render_component)

        return entity

    @staticmethod
    def create_game_board(world, board_res_name, pos):
        entity = EntityRecord(world, world.get_manager_by_type(EntityManager).generate_id())

        board_layout_res = ResourceManagerSingleton.instance().find_resource(board_res_name)
        board_width = board_layout_res.board_width
        board_height = board_layout_res.board_height
        tile_width = board_layout_res.tile_width
        tile_height = board_layout_res.tile_height

        pos_component = BoardTilePositionComponent(pos,
                                                   tile_width,
                                                   tile_height,
                                                   board_width,
                                                   board_height)
        entity.attach_component(pos_component)

        render_component = BoardRenderComponent(board_layout_res)
        entity.attach_component(render_component)

        #items_component = BoardItemsComponent(board_layout_res)
        #entity.attach_component(items_component)

        return entity

    @staticmethod
    def create_spawn_pipe(world, spawn_pos):
        pass

    @staticmethod
    def create_gem(world, gem_type, pos):
        entity = EntityRecord(world, world.get_manager_by_type(EntityManager).generate_id())

        gems_sprite_res = ResourceManagerSingleton.instance().find_resource("gems")

        render_component = GemsRenderComponent(gems_sprite_res, gem_type)
        entity.attach_component(render_component)

        physics_component = PhysicsComponent(pos)
        entity.attach_component(physics_component)

        return entity




