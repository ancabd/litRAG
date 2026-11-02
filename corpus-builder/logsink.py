"""Progress messages for the command-line tools, which the web app can also capture.

Every message goes to stderr (as before). Inside `with capture(fn):` it is also passed to fn,
on the same thread only, so a background job in the server can show the build's log while
other requests carry on.
"""
from __future__ import annotations

import sys
import threading
from contextlib import contextmanager
from typing import Callable

_local = threading.local()


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)
    sink = getattr(_local, "sink", None)
    if sink is not None:
        for line in str(msg).splitlines() or [""]:
            sink(line)


@contextmanager
def capture(fn: Callable[[str], None]):
    previous = getattr(_local, "sink", None)
    _local.sink = fn
    try:
        yield
    finally:
        _local.sink = previous
