from typing import TYPE_CHECKING

import mypkg.core as core

if TYPE_CHECKING:
    # Ensure type checking block is not recorded
    from numpy.typing import NDArray

    _: NDArray | None = None

core.run()
