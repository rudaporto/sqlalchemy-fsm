from functools import wraps, partial

from sqlalchemy.orm.instrumentation import register_class

import sqlalchemy.orm.events


class InstanceRef(object):
    """This class has to be passed to the dispatch call as instance.

    No idea why it is required.

    """

    __slots__ = ('target', )

    def __init__(self, target):
        self.target = target

    def obj(self):
        return self.target


FSM_EVENT_DISPATCHER_CACHE = {}


def get_class_bound_dispatcher(target_cls):
    """Python class-bound FSM dispatcher class."""
    try:
        out_val = FSM_EVENT_DISPATCHER_CACHE[target_cls]
    except KeyError:
        out_val = register_class(target_cls).dispatch
        FSM_EVENT_DISPATCHER_CACHE[target_cls] = out_val
    return out_val


class BoundFSMDispatcher(object):
    """Utility method that simplifies sqlalchemy event dispatch."""

    def __init__(self, instance):
        self.__ref = InstanceRef(instance)
        self.__cls_dispatcher = get_class_bound_dispatcher(type(instance))
        for fsm_handle in ('before_state_change', 'after_state_change'):
            # Precompute fsm handles
            # TODO: disable events
            # getattr(self, fsm_handle)
            pass

    def __getattr__(self, name):
        handle = partial(getattr(self.__cls_dispatcher, name), self.__ref)
        setattr(self, name, handle)
        return handle
        