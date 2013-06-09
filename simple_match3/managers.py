__author__ = 'magkbdev'

import entity


class IdentifierPool(object):

    def __init__(self):
        self._id_pool = []
        self._next_id = 0

    def checkout(self):
        if len(self._id_pool) > 0:
            return self._id_pool.pop()

        self._next_id += 1
        return self._next_id

    def checkin(self, id):
        self._id_pool.append(id)


class EntityManager(entity.EntityEventListener):

    def __init__(self):
        self._num_active = 0
        self._num_added = 0
        self._num_removed = 0

        self._entities = {}
        self._identity_pool = IdentifierPool()

    def get_entity_by_id(self, id):
        return self._entities[id]

    def on_entity_added(self, event_args):
        entity = event_args.entity_rec
        if entity is not None:
            self._num_active += 1
            self._num_added += 1
            self._entities[entity.id] = entity

    def on_entity_changed(self, event_args):
        pass

    def on_entity_removed(self, event_args):
        entity = event_args.entity_rec
        if entity is not None:
            self._entities[entity.id] = None
            self._identity_pool.checkin(entity.id)
            self._num_active -= 1
            self._num_removed += 1

    def generate_id(self):
        return self._identity_pool.checkout()






