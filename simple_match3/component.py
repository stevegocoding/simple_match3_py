import event


class ComponentSyncTriggerPred(object):
    
    def __init__(self, component_cls):
        self.cp_cls = component_cls

    def __call__(self, component):
        if component is not None:
            return isinstance(component, self.cp_cls)
        else:
            return False


class ComponentStateEventListener(object):

    def on_attached(self, event_args):
        pass

    def on_detached(self, event_args):
        pass


class Component(ComponentStateEventListener):

    _allocated_id = 0
    _components_registry = dict()

    def __init__(self):
        """
        The entity that this component is currently attached on
        """
        self._owner = None
        self._previous_owner = None

    def on_attached(self, state_event_args):
        pass

    def on_detached(self, state_event_args):
        pass

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

    def __str__(self):
        output_str = "{0} : {1}".format(type(self).__name__, "*" if self.need_sync else "")
        return output_str


class RenderComponent(Component):

    def __init__(self):
        Component.__init__(self)

    def render_frame(self):
        pass

    def update_frame(self, animation_ticks=1):
        pass