# goify

`goify` patches Python function objects with a `go()` method backed by
`gevent.spawn`.

```python
import goify

goify.patch_all()

def f():
    return "ok"

g = f.go()
print(g.get())
```
