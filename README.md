# goify

`goify` patches Python function objects with a `go()` method backed by
`gevent.spawn`, so regular functions can be launched in a Go-like style.

## Quick example

```python
import goify

goify.patch_all()

def side_effect():
    print("Side effect!")

side_effect.go()
# out: Side effect!
```

## How it works

`goify.patch_all()` does two things:

1. Calls `gevent.monkey.patch_all()` so standard library I/O becomes cooperative.
2. Patches `types.FunctionType` so every Python function gains a `go()` method.

The patching is process-wide for the current interpreter. After patching, any
new or existing Python function object can call `.go(...)`.

## How `go()` is implemented

The `go()` method is installed at runtime and is equivalent to:

```python
def go(self, *args, **kwargs):
    import gevent
    greenlet = gevent.spawn(self, *args, **kwargs)
    gevent.sleep(0)  # yield once so spawned work can start promptly
    return greenlet
```

Notes:

- `go()` returns a gevent `Greenlet`.
- Use `join()` or `get()` when you need to wait for completion.
- This is cooperative concurrency (greenlets), not native thread-based parallelism.
