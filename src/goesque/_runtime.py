import ctypes
import types

from gevent import monkey


class _PyMappingProxyObject(ctypes.Structure):
    _fields_ = [
        ("ob_refcnt", ctypes.c_ssize_t),
        ("ob_type", ctypes.c_void_p),
        ("mapping", ctypes.py_object),
    ]


def _mutable_type_dict(tp):
    proxy = tp.__dict__
    proxy_obj = _PyMappingProxyObject.from_address(id(proxy))
    return proxy_obj.mapping


def _install_go_on_type(tp):
    type_dict = _mutable_type_dict(tp)
    if "go" in type_dict:
        return

    def go(self, *args, **kwargs):
        import gevent

        greenlet = gevent.spawn(self, *args, **kwargs)
        # Yield once so newly spawned greenlets can start promptly.
        gevent.sleep(0)
        return greenlet

    type_dict["go"] = go
    py_type_modified = ctypes.pythonapi.PyType_Modified
    py_type_modified.argtypes = [ctypes.py_object]
    py_type_modified.restype = None
    py_type_modified(tp)


def patch_all(**kwargs):
    """Patch gevent monkey patches and add go() to functions/methods."""
    monkey.patch_all(**kwargs)
    _install_go_on_type(types.FunctionType)
    _install_go_on_type(types.MethodType)
