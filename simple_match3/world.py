__author__ = 'magkbdev'

import event


def notify_add_entity(listener, entity):
    listener.on_entity_added(event.EntityEventArgs(entity))


def notify_remove_entity(listener, entity):
    listener.on_entity_removed(event.EntityEventArgs(entity))


class EntityWorld(object):

    def __init__(self):

        self._added_entities = list()
        self._removed_entities = list()

        # {system_class : system_object}
        self._systems = {}
        # {manager_class : manager_class}
        self._managers = {}

    def add_entity(self, entity):
        self._added_entities.append(entity)

    def remove_entity(self, entity):
        self._removed_entities.append(entity)

    def add_system(self, system):
        system_class = type(system)
        self._systems[system_class] = system

    def add_manager(self, manager):
        manager_class = type(manager)
        self._managers[manager_class] = manager

    def get_system_by_type(self, system_class):
        return self._systems[system_class]

    def get_manager_by_type(self, manager_class):
        return self._managers[manager_class]

    def fire_entity_event(self, entity, action_func):
        for system in self._systems.values():
            action_func(system, entity)

        for manager in self._managers.values():
            action_func(manager, entity)

    def check(self, entities, action):
        if len(entities) > 0:
            for entity in entities:
                self.fire_entity_event(entity, action)

    def begin(self):
        self.check(self._added_entities, notify_add_entity)
        self.check(self._removed_entities, notify_remove_entity)

    def render(self):
        # Process all the systems
        for system in self._systems.values():
            system.render()

    def process(self):
        # Process all the systems
        for system in self._systems.values():
            system.process()

    def end(self):
        pass
