from typing import List, Tuple

import jax
import jax.lax as lax
import jax.numpy as jnp

from ..custom_types import Array, PyTree


def _stack_pytrees(*arrays):
    return jnp.stack(arrays)


def stack_pytrees(pytrees: List[PyTree]) -> PyTree:
    return jax.tree_map(_stack_pytrees, *pytrees)


class ContainerMeta(type):
    def __new__(cls, name, bases, dict):
        assert "_reverse_lookup" not in dict
        _dict = {}
        _reverse_lookup = {}
        i = 0
        for key, value in dict.items():
            if key.startswith("__") and key.endswith("__"):
                _dict[key] = value
            else:
                _dict[key] = i
                _reverse_lookup[i] = value
                i += 1
        _dict["_reverse_lookup"] = _reverse_lookup
        return super().__new__(cls, name, bases, _dict)

    def __getitem__(cls, item):
        return cls._reverse_lookup[item]


def _fill_forward(
    last_observed_yi: Array["channels"], yi: Array["channels"]  # noqa: F821
) -> Tuple[Array["channels"], Array["channels"]]:  # noqa: F821
    yi = jnp.where(jnp.isnan(yi), last_observed_yi, yi)
    return yi, yi


@jax.jit
def fill_forward(
    ys: Array["times", "channels"]  # noqa: F821
) -> Array["times, channels"]:  # noqa: F821
    _, ys = lax.scan(_fill_forward, ys[0], ys)
    return ys
