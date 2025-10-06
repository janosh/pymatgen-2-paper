import typing
from typing import TYPE_CHECKING

import mypkg.core as core

if typing.TYPE_CHECKING:
    # Ensure type checking import is not recorded
    from numpy.typing import NDArray

    _: NDArray | None = None

if TYPE_CHECKING:
    from numpy.typing import NDArray

    _: NDArray | None = None


core.run()


# Check indented code block
def foo():
    core.run()
