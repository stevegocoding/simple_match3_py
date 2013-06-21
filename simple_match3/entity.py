import uuid
import event


class EntityEventListener(object):

    def on_entity_added(self, event_args):
        pass

    def on_entity_removed(self, event_args):
        pass

    def on_entity_changed(self, event_args):
        pass


class EntityRecord(object):

    def __init__(self, world, id, name="unnamed_entity"):

        self.name = name

        # Entity Registry
        self.entity_registry = EntityRegistry.get_current()

        # System sets
        self._systems_cls = set()

        # Components Types Set
        self._components_classes_set = set()

        self._world = world
        self._id = id

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self, value):
        #setattr(self, "name", value);
        self._name = value

    @property
    def id(self):
        return self._id

    def get_components_classes_set(self):
        return self._components_classes_set

    def get_systems_classes_set(self):
        return self._systems_cls

    def has_component(self, component):
        if component is not None and self.entity_registry is not None:
            comps_dict = self.entity_registry.get_components(self)
            return component in comps_dict.values
        else:
            raise Exception("Component or Entity Registry is None!")

    def get_component(self, component_cls):
        return self.entity_registry.get_component(self, component_cls)

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

    def add_to_world(self):
        self._world.add_entity(self)

    def remove_from_world(self):
        self._world.remove_entity(self)


    @staticmethod
    def get_guid():
        return str(uuid.uuid())

    @staticmethod
    def create(name, entity_registry, components_classes_set=None):
        entity_rec = EntityRecord(name, entity_registry)

        if components_classes_set is not None:
            for component_cls in components_classes_set:
                entity_rec.attach_component(component_cls())

        return entity_rec


class EntityRecordStore(object):
    def __init__(self):
        # { entity_record : {component_cls : component} }
        self.records = dict()

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
                entity_rec.get_components_classes_set().add(cp_cls)

                if component.owner is None or component.owner != entity_rec:
                    component.owner = entity_rec

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
                entity_rec.get_components_classes_set().remove(comp_cls)
                comp_removed = True
        
        if component.owner is not None:
            component.owner = None

        return comp_removed

    def on_entered(self, entity_event_args):
        if self.on_entity_entered is not None:
            self.on_entity_entered(entity_event_args)

    def on_removed(self, entity_event_args):
        if self.on_entity_removed is not None:
            self.on_entity_removed(entity_event_args)

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

    def contains(self, entity_rec):
        return entity_rec in self.records


class EntityRegistry(object):

    _default_registry = EntityRecordStore()
    _active_registry = _default_registry

    @staticmethod
    def get_current():
        return EntityRegistry._active_registry


class Aspect(object):

    def __init__(self):
        self._all = set()
        self._exclude = set()

    @property
    def all(self):
        return self._all

    @all.setter
    def all(self, components_cls):
        self._all = components_cls

    @property
    def exclude(self):
        return self._exclude

    @exclude.setter
    def exclude(self, components_cls):
        self._exclude = set(components_cls)

    @staticmethod
    def create_aspect_for_all(components_cls):
        aspect = Aspect()
        aspect.all = set(components_cls)
        return aspect

    @staticmethod
    def create_empty():
        aspect = Aspect()
        return aspect


class EntitySystem(EntityEventListener):

    def __init__(self, aspect):
        self._aspect = aspect
        self._all = aspect.all
        self._exclude = aspect.exclude

        self._active_entities = []

    def begin(self):
        """
        Called before processing of entities begins.
        """
        pass

    def render(self):
        pass

    def process(self):
        if self.check_processing():
            self.begin()
            self.process_entities(self._active_entities)
            self.end()

    def end(self):
        pass

    def on_entity_added(self, event_args):
        self.check(event_args.entity_rec)

    def on_entity_removed(self, event_args):
        self.check(event_args.entity_rec)

    # To be overridden
    def on_inserted_entity(self, entity):
        """
        Called if the system has received a entity it is interested in, e.g. created or a component
        was added to it.
        """
        pass

    # To be overridden
    def on_removed_entity(self, entity):
        """
        Called if a entity was removed from this system, e.g. deleted or had one of it's components
        removed.
        """
        pass

    def check_processing(self):
        """
        Return true if the system should be processed, false if not.
        """
        pass

    def process_entities(self, entities):
        """
        Any implementing entity system must implement this method and the logic
        to process the given entities of the system.
        """
        pass

    def initialize(self):
        pass

    def insert_entity(self, entity):
        self._active_entities.append(entity)
        entity.get_systems_classes_set().add(type(self))
        self.on_inserted_entity(entity)

    def remove_entity(self, entity):
        self._active_entities.remove(entity)
        entity.get_systems_classes_set().remove(type(self))
        self.on_removed_entity(entity)

    def check(self, entity_rec):
        """
        Will check if the entity is of interest to this system.
        """
        system_cls = type(self)
        contains = system_cls in entity_rec.get_systems_classes_set()
        interested = True

        if len(self._all) > 0 and \
                (self._all > entity_rec.get_components_classes_set() or
                 self._all.isdisjoint(entity_rec.get_components_classes_set())):
            interested = False

        if interested and not contains:
            self.insert_entity(entity_rec)
        elif not interested and contains:
            self.remove_entity(entity_rec)