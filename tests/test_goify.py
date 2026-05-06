import time

import gevent

import goify


def test_function_has_go_after_patch_all():
    goify.patch_all()

    def f():
        return 123

    greenlet = f.go()
    assert greenlet.get(timeout=1) == 123


def test_functions_execute_concurrently():
    goify.patch_all()

    order = []

    def task(name, delay):
        gevent.sleep(delay)
        order.append(name)
        return name

    start = time.perf_counter()
    g1 = task.go("a", 0.2)
    g2 = task.go("b", 0.2)
    gevent.joinall([g1, g2], timeout=1)
    elapsed = time.perf_counter() - start

    assert g1.ready() and g2.ready()
    assert sorted(order) == ["a", "b"]
    assert elapsed < 0.35


def test_go_yields_once_for_new_greenlet():
    goify.patch_all()
    marker = []

    def task():
        marker.append("ran")

    g = task.go()
    assert marker == ["ran"]
    g.join(timeout=1)
