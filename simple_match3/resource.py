import pyglet.resource
import pyglet.image
import pyglet.gl as gl
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


class ResourceManager(object):

    def __init__(self):
        # {resource_name : resource}
        self._resources = {}

    def register_spritesheet(self, spritesheet_res):
        self._resources[spritesheet_res.name] = spritesheet_res

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


class GameAssetArchiveLoader(pyglet.resource.Loader):
    """
    This loader is responsible for loading the game asset from an zip archive
    The asset data is organized level by level. First it loaders a header xml file right away.
    All the other level data is loaded in a lazy fashion.
    """

    def __init__(self, path=None, script_home=None, header_name="header.xml"):
        pyglet.resource.Loader.__init__(self, path, script_home)

        self._levels = {}
        self.load_header_xml(header_name)

    def load_header_xml(self, name):
        header_file = self.file(name)
        self.parse_header(header_file)

    def parse_header(self, header_file):
        with open(header_file, "r") as file_handle:
            tree = ElementTree.parse(file_handle)
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

        level_name = level_elem.get("name")
        self._levels[level_name] = \
            GameLevelAssetData(level_name, gfx_resources, sound_resources, font_resources, map_resources)

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
                file_handle = self.file(gfx_name)
                if level.gfx_resources[gfx_name]["type"] == "spritesheet":
                    res = self.load_spritesheet_resource(file_handle, gfx_name)
                    ResourceManagerSingleton.instance().register_spritesheet(res)

            # Load all the sound resources in this level
            for sound_name in level.sound_resources:
                pass

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
        atlas_texture = self.texture(image_atlas_elem.get("file"))
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
