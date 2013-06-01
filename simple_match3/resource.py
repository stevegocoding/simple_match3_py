import os
import pyglet.resource
import cocos.tiles
from xml.etree import ElementTree


class SpriteSheetResource(cocos.tiles.Resource):

    def __init__(self, filename):
        cocos.tiles.Resource.__init__(self, filename)
        self.animations = {}

    def handle(self, tag):
        for child in tag:
            if child.tag == "imageatlas":
                self.factories[child.tag](self, child)
            if child.tag == "animation":
                self.factories[child.tag](self, child)

    def add_animation(self, state, frame_list):
        self.animations[state] = frame_list

    def get_frame_image(self, state, frame):
        if state in self.animations and frame < len(self.animations[state]):
            image = self.get_resource(self.animations[state][frame])
            return image
        return None

    def get_frames_count(self, state):
        if state in self.animations:
            return len(self.animations[state])
        return 0

    def __str__(self):
        return self.animations.__str__()


@cocos.tiles.Resource.register_factory('animation')
def sprite_animation_factory(resource, tag):

    for seq in tag:
        if seq.tag != "sequence":
            raise ValueError("invalid child")

        seq_name = seq.get("name")
        frames = []
        for frame in seq:
            if frame.tag != "frame":
                raise ValueError("invalid frame")

            frame_id = frame.get("id")
            if frame_id is None:
                raise ValueError("invalid frame ID")

            frame_img = resource.get_resource(frame_id)
            if frame_img is None:
                raise ValueError("invalid frame image")

            frames.append(frame_id)

        resource.add_animation(seq_name, frames)


def load_spritesheet(filename):
    """
    Load resource(s) defined in the indicated XML file.
    """
    # make sure we can find files relative to this one
    dirname = os.path.dirname(filename)
    if dirname and dirname not in pyglet.resource.path:
        pyglet.resource.path.append(dirname)
        pyglet.resource.reindex()

    if filename in cocos.tiles._cache:
        if cocos.tiles._cache[filename] is cocos.tiles._NOT_LOADED:
            raise cocos.tiles.ResourceError('Loop in tile map files loading "%s"' % filename)
        return cocos.tiles._cache[filename]

    cocos.tiles._cache[filename] = cocos.tiles._NOT_LOADED
    resource = SpriteSheetResource(filename)
    tree = ElementTree.parse(resource.path)
    root = tree.getroot()
    if root.tag != 'resource':
        raise cocos.tiles.ResourceError('document is <%s> instead of <resource>' % root.name)
    resource.handle(root)

    cocos.tiles._cache[filename] = resource
    return resource


SpriteSheetResource.register_factory("imageatlas")
SpriteSheetResource.register_factory("animation")