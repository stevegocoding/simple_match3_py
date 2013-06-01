import uuid
import cocos.cocosnode
from src.framework import graphics, event


class EntityDefinition(object):
    def __init__(self):
        # Definitions is like: {def_name : list of component_cls}
        self.definitions = dict()

    def define(self, def_name, component_cls_lst):
        if def_name is not None and component_cls_lst is not None:
            self.definitions[def_name] = component_cls_lst

    def undefine(self, def_name):
        if def_name in self.definitions:
            del self.definitions[def_name]

    def make(self, def_name, entity_rec):
        if def_name in self.definitions:
            component_cls_lst = self.definitions[def_name]
            for component_cls in component_cls_lst:
                    entity_rec.attach_component(component_cls())
            return entity_rec
        return entity_rec


class EntityRecord(cocos.cocosnode.CocosNode):

    def __init__(self, name, entity_registry):
        cocos.cocosnode.CocosNode.__init__(self)

        self.name = name

        # Entity Registry
        self.entity_registry = entity_registry

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self, value):
        #setattr(self, "name", value);
        self._name = value

    def has_component(self, component):
        if component is not None and self.entity_registry is not None:
            comps_dict = self.entity_registry.get_components(self)
            return component in comps_dict.values
        else:
            raise Exception("Component or Entity Registry is None!")

    def get_component(self, component_cls):
        return self.entity_registry.get_component(self, component_cls)

    def need_sync(self):
        """
        The entity is considered out-of-sync when it is not registered
        in a registry, and/or has no name
        """
        return (self.name is None or 
                self.entity_registry is None or
                not self.entity_registry.contains(self))

    def synchronize(self):
        if self.entity_registry is not None:
            if not self.entity_registry.contains(self):
                self.entity_registry.enter(self)

    def attach_component(self, component):
        if self.entity_registry is not None:
            self.entity_registry.add(self, component)

    def __str__(self):
        comps_dict = self.entity_registry.get_components(self)
        s_lst = []
        if comps_dict is not None and len(comps_dict) > 0:
            comps = comps_dict.values()
            for cp in comps:
                s = "{0} | ".format(str(cp))
                s_lst.append(s)

        return "".join(s_lst)

    def visit(self):
        self.render()
        cocos.cocosnode.CocosNode.visit(self)

    def draw(self):
        pass

    def process(self):
        print "EntityRecord process()"

    def render(self):
        renderer = self.entity_registry.get_component(self, graphics.SpriteRenderer)
        if renderer is not None:
            print "EntityRecord render()"
            renderer.update_frame(graphics.GameScene.frame_count())
            renderer.render_frame()

    def on_enter(self):
        pass


class Entity(object):

    # Entity Definitions {def_name : list_of_component_classes}
    _definitions = EntityDefinition()

    @staticmethod
    def create(name, entity_registry, components):
        entity_rec = EntityRecord(name, entity_registry)

        entity_rec.synchronize()

        if components is not None:
            for cp in components:
                entity_rec.attach_component(cp)

        return entity_rec

    @staticmethod
    def create_from_def(def_name, name):
        entity_rec = Entity.create(name, EntityRegistry._active_registry, None)
        return Entity._definitions.make(def_name, entity_rec)

    @staticmethod
    def define(def_name, component_classes):
        Entity._definitions.define(def_name, component_classes)

    @staticmethod
    def undefine(def_name):
        Entity._definitions.undefine(def_name)

    @staticmethod
    def get_guid():
        return str(uuid.uuid())


class EntityRecordStore(object):
    def __init__(self):
        # { entity_record : {component_cls : component} }
        self.records = dict()

        # List of components need to be synced
        self._desynced_components = list()

        # Dictionary of the triggers and handlers
        # _triggers is a dictionary like {trigger_predicate : event_handler}
        self._triggers = dict()

        # Handlers
        self.on_entity_entered = None
        self.on_entity_removed = None

    def enter(self, entity_rec):
        """
        Register an entity with no components
        """
        self.add(entity_rec, None)

    def drop(self, entity_rec):
        """
        Un-register an entity and returns 'True' if it was successfully
        dropped. 
        """
        if entity_rec is None:
            return False

        comps_dict = self.get_components(entity_rec)
        if comps_dict is not None and len(comps_dict) > 0:
            cp_instances = comps_dict.values()

            # Remove the components first
            for cp in cp_instances:
                self.remove(entity_rec, cp)

        # Remove the entity
        del self.records[entity_rec]
        entity_dropped = True

        self.on_removed(event.EntityEventArgs(entity_rec))

        return entity_dropped

    def add(self, entity_rec, component):
        """
        Attaches the specified component to an entity.
        """
        entity_registered = True
        component_attached = False

        if component is not None:
            old_owner = component.owner
            if old_owner is not None and old_owner != entity_rec:
                self.remove(old_owner, component)

        # Get the components registered for this entity record
        # If there is none, then create one
        comps_dict = self.get_components(entity_rec)
        if comps_dict is None:
            comps_dict = dict()
            entity_registered = False
            self.records[entity_rec] = comps_dict

        if component is not None:
            cp_cls = type(component)
            if cp_cls not in comps_dict:
                comps_dict[cp_cls] = component

                if component.owner is None or component.owner != entity_rec:
                    component.owner = entity_rec

                self.prepare_components_for_sync(component)

                component_attached = True

        # If this entity is just registered, we fire the on_enter for this entity
        if not entity_registered:
            self.on_entered(event.EntityEventArgs(entity_rec))

        return component_attached

    def remove(self, entity_rec, component):
        """
        Detach the specified component from an entity.
        Returns "True" if it was successful.
        """
        if entity_rec is None or component is None:
            return False

        if component.owner is not None and component.owner != entity_rec:
            return False

        comp_removed = False
        comps_dict = self.get_components(entity_rec)
        if comps_dict is not None and len(comps_dict) > 0:
            comp_cls = type(component)

            if comp_cls in comps_dict:
                del comps_dict[comp_cls]
                comp_removed = True
        
        if component.owner is not None:
            component.owner = None

        self.prepare_components_for_sync(component)

        return comp_removed

    def on_entered(self, sync_event_args):
        if self.on_entity_entered is not None:
            self.on_entity_entered(sync_event_args)

    def on_removed(self, sync_event_args):
        if self.on_entity_removed is not None:
            self.on_entity_removed(sync_event_args)

    def get_components(self, entity_rec):
        if entity_rec in self.records:
            return self.records[entity_rec]
        else:
            return None

    def get_component(self, entity_rec, component_cls):
        components_dict = self.get_components(entity_rec)

        if component_cls in components_dict:
            return components_dict[component_cls]
        return None

    def set_trigger(self, predicate, handler):
        self._triggers[predicate] = handler

    def clear_trigger(self, predicate):
        if predicate in self._triggers:
            del self._triggers

    def prepare_components_for_sync(self, component):
        """
        """
        if component not in self._desynced_components:
            self._desynced_components.append(component)

    def need_sync(self):
        """
        This registry is considered out of sync as soon as there are 
        components that have not yet been run through triggers
        """
        return self._desynced_components is not None and len(self._desynced_components) > 0

    def synchronize(self):
        if len(self._desynced_components) > 0:
            for trigger_pred in self._triggers.keys():
                comps = []
                for cp in self._desynced_components:
                    if trigger_pred(cp):
                        comps.append(cp)

                if len(comps) > 0:
                    self._triggers[trigger_pred](event.ComponentSyncEventArgs(comps))

            del self._desynced_components[0:len(self._desynced_components)]

    def contains(self, entity_rec):
        return entity_rec in self.records


class EntityRegistry(object):

    _default_registry = EntityRecordStore()
    _active_registry = _default_registry

    @staticmethod
    def get_current():
        return EntityRegistry._active_registry