import pyglet.resource
import pyglet.image
import pyglet.gl as gl

import json
from xml.etree import ElementTree


class GameLevelAssetData(object):

    def __init__(self, name, gfx_resources, sound_resources, font_resources, map_resources):
        self._name = name
        self._gfx_resources = gfx_resources
        self._sound_resources = sound_resources
        self._font_resources = font_resources
        self._map_resources = map_resources

        self._is_global = False
        self._loaded = False

    @property
    def name(self):
        return self._name

    @property
    def gfx_resources(self):
        return self._gfx_resources

    @property
    def sound_resources(self):
        return self._sound_resources

    @property
    def font_resources(self):
        return self._font_resources

    @property
    def map_resources(self):
        return self._map_resources

    @property
    def is_global(self):
        return self._is_global

    @is_global.setter
    def is_global(self, val):
        self._is_global = val

    @property
    def loaded(self):
        return self._loaded

    @loaded.setter
    def loaded(self, val):
        self._loaded = val


class ResourceEventListener(object):

    def on_loaded(self, event_args):
        pass

    def on_unloaded(self, event_args):
        pass

    def on_registered(self, event_args):
        pass


class Resource(ResourceEventListener):

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


class SpriteSheetResource(Resource):

    def __init__(self, name):
        Resource.__init__(self, name)

        self._images = {}
        self._animations = {}

    def add_image(self, id, texture):
        self._images[id] = texture

    def add_animation_sequence(self, seq_name, frames):
        self._animations[seq_name] = frames

    def get_frames_count(self, state):
        if state in self._animations:
            return len(self._animations[state])

    def get_frame_image(self, state, frame):
        if state in self._animations and frame < len(self._animations[state]):
            image = self._images[self._animations[state][frame]]
            return image
        return None


class MapLayer(object):
    def __init__(self, name, map_type, width, height, image_name, tiles, z):
        self._name = name
        self._width = width
        self._height = height
        self._image_name = image_name
        self._z_order = z
        self._type = map_type

        self._tiles = []
        if tiles:
            for tile in tiles:
                self._tiles.append(tile-1)

    @property
    def name(self):
        return self._name

    @property
    def z_order(self):
        return self._z_order

    @property
    def image_name(self):
        return self._image_name

    @property
    def tiles(self):
        return self._tiles

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def type(self):
        return self._type


class MapTileset(object):
    def __init__(self, name, texture, tile_width, tile_height):
        self._name = name
        self._tileset_texture = texture
        self._tile_width = tile_width
        self._tile_height = tile_height
        self._num_tiles_x = texture.width / tile_width
        self._num_tiles_y = texture.height / tile_height

    @property
    def name(self):
        return self._name

    @property
    def tileset_texture(self):
        return self._tileset_texture

    @property
    def tile_width(self):
        return self._tile_width

    @property
    def tile_height(self):
        return self._tile_height

    @property
    def num_tiles_x(self):
        return self._num_tiles_x

    @property
    def num_tiles_y(self):
        return self._num_tiles_y


class TiledBoardResource(Resource):

    def __init__(self, name):
        Resource.__init__(self, name)

        # texture regions for each tile
        self._tiles_images = []
        self._image_layer_textures = {}

        #
        self._layers = []
        self._layer_properties = {}

        self._tilesets = []
        self._tileset_properties = {}

    def setup_tileset(self, name, texture, tile_width, tile_height, properties):
        tileset = MapTileset(name, texture, tile_width, tile_height)
        self._tilesets.append(tileset)

        self._tileset_properties[name] = properties

        num_tiles = tileset.num_tiles_x * tileset.num_tiles_y
        for i in range(num_tiles):
            tile_y = i / tileset.num_tiles_x
            tile_x = i - tile_y * tileset.num_tiles_x
            offset_x = tile_x * tile_width
            offset_y = texture.height - (tile_y+1) * tile_height
            tex = tileset.tileset_texture.get_region(offset_x, offset_y, tile_width, tile_height)
            self._tiles_images.append(tex)

    def add_map_layer(self, z, **kwargs):
        property = kwargs["properties"]
        width = property["width"]
        height = property["height"]
        name = kwargs["name"]
        type = kwargs["type"]
        image = None
        if "image" in kwargs:
            image = kwargs["image"]
        tiles = None
        if "data" in kwargs:
            tiles = kwargs["data"]
        layer = MapLayer(name, type, int(width), int(height), image, tiles, int(z))
        self._layers.append(layer)
        self.sort_layers()

    def get_tile_image(self, tile_idx):
        return self._tiles_images[tile_idx]

    def add_image_layer_texture(self, layer_name, texture):
        self._image_layer_textures[layer_name] = texture

    def get_image_layer_texture(self, layer_name="background"):
        if layer_name in self._image_layer_textures:
            return self._image_layer_textures[layer_name]
        return None

    def sort_layers(self):
        if len(self._layers) > 1:
            self._layers.sort(key=lambda x: x.z_order)

    def add_layer_properties(self, name, properties):
        self._layer_properties[name] = properties

    def get_layer_properties(self, name):
        return self._layer_properties[name]

    def get_tileset_properties(self, name):
        return self._tileset_properties[name]

    @property
    def board_origin(self):
        origin_x = int(self._layer_properties["board_layer"]["origin_x"])
        origin_y = int(self._layer_properties["board_layer"]["origin_y"])
        return origin_x, origin_y

    @property
    def board_width(self):
        return int(self._layer_properties["board_layer"]["width"])

    @property
    def board_height(self):
        return int(self._layer_properties["board_layer"]["height"])

    @property
    def tile_width(self):
        return int(self._tilesets[0].tile_width)

    @property
    def tile_height(self):
        return int(self._tilesets[0].tile_height)

    @property
    def layers(self):
        return self._layers

    @property
    def tilesets(self):
        return self._tilesets


class SimpleTextureResource(Resource):

    def __init__(self, name, texture):
        Resource.__init__(self, name)

        self._texture = texture

    @property
    def width(self):
        return self._texture.width

    @property
    def height(self):
        return self._texture.height

    @property
    def texture(self):
        return self._texture


class ResourceManager(object):

    def __init__(self):
        # {resource_name : resource}
        self._resources = {}

    def register_spritesheet(self, spritesheet_res):
        self._resources[spritesheet_res.name] = spritesheet_res

    def register_map(self, map_res):
        self._resources[map_res.name] = map_res

    def register(self, res):
        self._resources[res.name] = res

    def find_resource(self, name):
        if name in self._resources:
            return self._resources[name]
        return None


class ResourceManagerSingleton(object):

    res_mgr_instance = None

    def __init__(self):
        if ResourceManagerSingleton.res_mgr_instance is None:
            ResourceManagerSingleton.res_mgr_instance = ResourceManager()

    @staticmethod
    def instance():
        return ResourceManagerSingleton.res_mgr_instance


ResourceManagerSingleton()

ROOT_TAG_NAME = "GameAssetArchive"
LEVEL_TAG_NAME = "level"
GFX_TAG_NAME = "gfx"
SOUND_TAG_NAME = "sound"
FONT_TAG_NAME = "font"
MAP_TAG_NAME = "map"

GFX_PATH_PREFIX = "gfx"
SOUND_PATH_PREFIX = "sound"
FONT_PATH_PREFIX = "font"
MAP_PATH_PREFIX = "map"


class GameAssetArchiveLoader(pyglet.resource.Loader):
    """
    This loader is responsible for loading the game asset from an zip archive
    The asset data is organized level by level. First it loaders a header xml file right away.
    All the other level data is loaded in a lazy fashion.
    """

    def __init__(self, path=None, script_home=None, header_prefix="assets", header_name="header.xml"):
        pyglet.resource.Loader.__init__(self, path, script_home)

        self._levels = {}

        self._assets_path_prefix = header_prefix
        header_path = "/".join([header_prefix, header_name])
        self.load_header_xml(header_path)

    def get_resource_path(self, prefix, name):
        res_path = "/".join([self._assets_path_prefix, prefix, name])
        return res_path

    def load_header_xml(self, name):
        header_file = self.file(name)
        self.parse_header(header_file)

    def parse_header(self, header_file):
        tree = ElementTree.parse(header_file)
        root = tree.getroot()
        if root.tag == ROOT_TAG_NAME:
            for child in root.findall(LEVEL_TAG_NAME):
                self.parse_level_element(child)

    def parse_level_element(self, level_elem):
        gfx_resources = {}
        sound_resources = {}
        font_resources = {}
        map_resources = {}
        for gfx_elem in level_elem.findall(GFX_TAG_NAME):
            gfx_resources[gfx_elem.get("name")] = gfx_elem.attrib

        for sound_elem in level_elem.findall(SOUND_TAG_NAME):
            sound_resources[sound_elem.get("name")] = sound_elem.attrib

        for font_elem in level_elem.findall(FONT_TAG_NAME):
            font_resources[font_elem.get("name")] = font_elem.attrib

        for map_elem in level_elem.findall(MAP_TAG_NAME):
            map_resources[map_elem.get("name")] = map_elem.attrib

        level_name = level_elem.get("name")
        self._levels[level_name] = \
            GameLevelAssetData(level_name,
                               gfx_resources,
                               sound_resources,
                               font_resources,
                               map_resources)

    def find_level_data_by_res_name(self, name, type_name):
        for level in self._levels.values():
            if type_name == GFX_TAG_NAME and name in level.gfx_resources:
                return level

            elif type_name == SOUND_TAG_NAME and name in level.sound_resources:
                return level
            else:
                return None

    def level(self, name):
        """
        Load all the data of a level, including gfx, sounds, fonts etc.
        """
        if name in self._levels:
            level = self._levels[name]

            # Load all the graphics resources in this level
            for gfx_name in level.gfx_resources:
                file_handle = self.file(self.get_resource_path(GFX_PATH_PREFIX, gfx_name))
                if level.gfx_resources[gfx_name]["type"] == "spritesheet":
                    res = self.load_spritesheet_resource(file_handle, gfx_name)
                    ResourceManagerSingleton.instance().register_spritesheet(res)
                elif level.gfx_resources[gfx_name]["type"] == "texture":
                    res = self.load_simple_texture(file_handle, gfx_name)
                    ResourceManagerSingleton.instance().register(res)

            # Load all the sound resources in this level
            for sound_name in level.sound_resources:
                pass

            for map_name in level.map_resources:
                file_handle = self.file(self.get_resource_path(MAP_PATH_PREFIX, map_name))
                if level.map_resources[map_name]["type"] == "json":
                    res = self.load_tiled_map_json(file_handle, map_name)
                    ResourceManagerSingleton.instance().register_map(res)

            #TODO

    def load_spritesheet_resource(self, file_handle, name):
        """
        Parse the spritesheet XML file and actually load the data
        """
        tree = ElementTree.parse(file_handle)
        root = tree.getroot()
        image_atlas_elem = root.find("imageatlas")
        animation_atlas_elem = root.find("animation")

        spritesheet_res = SpriteSheetResource(name)

        # Load the spritesheet image as a texture
        texture_path = self.get_resource_path(GFX_PATH_PREFIX, image_atlas_elem.get("file"))
        atlas_texture = self.texture(texture_path)
        atlas_width, atlas_height = map(int, image_atlas_elem.get('size').split('x'))

        for child in image_atlas_elem.findall("image"):
            name = child.get("id")
            width, height = map(int, child.get('size').split('x'))
            x, y = map(int, child.get('offset').split(','))
            image = atlas_texture.get_region(x, y, width, height)

            # set texture clamping to avoid mis-rendering subpixel edges
            gl.glBindTexture(image.texture.target, image.texture.id)
            gl.glTexParameteri(image.texture.target, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
            gl.glTexParameteri(image.texture.target, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
            spritesheet_res.add_image(name, image)

        # Load the animations
        for child in animation_atlas_elem.findall("sequence"):
            seq_name = child.get("name")
            frames = []
            for frame in child.findall("frame"):
                frames.append(frame.get("id"))

            spritesheet_res.add_animation_sequence(seq_name, frames)

        return spritesheet_res

    def load_tiled_map_json(self, file_handle, name):
        map_obj = json.load(file_handle)
        map_res = TiledBoardResource(name)

        self._load_tilesets(map_res, map_obj)
        self._load_layers(map_res, map_obj)

        return map_res

    def _load_tilesets(self, map_res, map_obj):
        num_tilesets = len(map_obj["tilesets"])

        for i in range(num_tilesets):
            tileset_data = map_obj["tilesets"]
            tileset_name = tileset_data[i]["name"]
            tileset_image_file = tileset_data[i]["image"]
            texture_path = self.get_resource_path(MAP_PATH_PREFIX, tileset_image_file)
            tileset_tex = self.texture(texture_path)

            tileset_properties = tileset_data[i]["properties"]
            tile_width = tileset_data[i]["tilewidth"]
            tile_height = tileset_data[i]["tileheight"]
            map_res.setup_tileset(tileset_name, tileset_tex, tile_width, tile_height, tileset_properties)

    def _load_layers(self, map_res, map_obj):
        z_order = 0
        for layer in map_obj["layers"]:

            map_res.add_layer_properties(layer["name"], layer["properties"])
            map_res.add_map_layer(z_order, **layer)

            if layer["type"] == "imagelayer":
                image_file = layer["image"]
                texture_path = self.get_resource_path(MAP_PATH_PREFIX, image_file)
                tex = self.texture(texture_path)
                map_res.add_image_layer_texture(layer["name"], tex)

            z_order += 1

    def load_simple_texture(self, file_handle, name):
        res_obj = json.load(file_handle)

        texture_file = res_obj["file"]
        texture_path = self.get_resource_path(GFX_PATH_PREFIX, texture_file)
        texture = self.texture(texture_path)

        tex_res = SimpleTextureResource(name, texture)

        return tex_res