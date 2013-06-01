from src.framework import event


class ComponentSyncTriggerPred(object):
    
    def __init__(self, component_cls):
        self.cp_cls = component_cls

    def __call__(self, component):
        if component is not None:
            return isinstance(component, self.cp_cls)
        else:
            return False


class Component(object):

    _allocated_id = 0
    _components_registry = dict()

    def __init__(self):
        """
        The entity that this component is currently attached on
        """
        self._owner = None
        self._previous_owner = None

        # Delegate called when this component is attached or detached
        self.on_component_attached = None
        self.on_component_detached = None

    def draw(self):
        pass

    def process(self):
        pass

    def on_attached(self, state_event_args):
        if self.on_component_attached is not None:
            self.on_component_attached(state_event_args)

    def on_detached(self, state_event_args):
        if self.on_component_dettached is not None:
            self.on_component_dettached(state_event_args)

    def need_sync(self):
        """
        The component is considered out-of-sync if it is not attached
        to any entity
        """
        return self.owner is None or self.owner.has_component(self)

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        require_sync = (self._previous_owner is not None and 
                        self._previous_owner.has_component(self))

        if require_sync:
            raise Exception("Component has to be synchronized before further\
                            changes can happen")
        else:
            if self._owner is None or self._owner != value:
                self._previous_owner = self._owner
                self._owner = value

                state_change_event = event.ComponentStateEventArgs(self._owner, self._previous_owner)

                if self.owner is not None:
                    self.on_attached(state_change_event)
                else:
                    self.on_dettached(state_change_event)

    def synchronize(self):
        """
        Ensures that the component becomes synchronized by
        establishing the appropriate relation to its parent entity.
        """
        if self.owner is not None:
            if not self.owner.has_component(self):
                self.owner.attach_component(self)
                if self.on_component_attached is not None:
                    self.on_component_attached(event.ComponentStateEventArgs(self.owner, self._previous_owner))
        else:
            if self._previous_owner is not None:
                removed = self._previous_owner.remvoe(self)
                if removed is True:
                    if self.on_component_detached is not None:
                        self.on_component_detached(event.ComponentStateEventArgs(self.owner, self._previous_owner))
                        self._previous_owner = None

    @classmethod
    def create(cls, component_cls):
        return component_cls()

    @classmethod
    def register(cls, component_cls):
        if Component.is_registered(component_cls) is not True:
            Component._components_registry[Component._allocated_id] = component_cls
            Component._allocated_id += 1

    @classmethod
    def is_registered(cls, component_cls):
        return component_cls in Component._components_registry.values()

    def __str__(self):
        output_str = "{0} : {1}".format(type(self).__name__, "*" if self.need_sync else "")
        return output_str