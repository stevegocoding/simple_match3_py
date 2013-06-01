class EventArgs(object):
    pass


class EventHook(object):
    def __init__(self, handlers = None):
        if handlers is None:
            self.handlers = []
        else:
            self.handlers = handlers

    def add_handler(self, handler):
        self.handlers.append(handler) 

    def __call__(self, event_args):
        for f in self.handlers:
            f(event_args)


class ComponentSyncEventArgs(EventArgs):
    def __init__(self, cp_list):
        super(ComponentSyncEventArgs, self).__init__()
        self.cp_list = cp_list

    @property
    def cp_list(self):
        return self.cp_list

    def get_dettached_cps(self):
        cps = []
        for cp in self.cp_list:
            if cp.need_sync:
                cps.append(cp)
        return cps

    def get_attached_cps(self):
        cps = []
        for cp in self.cp_list:
            if not cp.need_sync:
                cps.append(cp)
        return cps


class EntityEventArgs(EventArgs):
    def __init__(self, entity_rec):
        super(EntityEventArgs, self).__init__()
        self._entity_rec = entity_rec

    @property
    def entity_rec(self):
        return self._entity_rec

    @entity_rec.setter
    def entity_rec(self, value):
        self._entity_rec = value


class ComponentStateEventArgs(EntityEventArgs):
    def __init__(self, owner, previous_owner):
        super(ComponentStateEventArgs, self).__init__(owner)
        self._owner = owner
        self._previouse_owner = previous_owner

    @property
    def previous_owner(self):
        return self._previouse_owner

    @property
    def owner(self):
        return self._owner
