"""" Core Test """
import asyncio
import logging
from triton_telemetry import core


logging.basicConfig(level=logging.INFO)

# asyncio.run(main())
result = asyncio.run(core.scan_all_providers(
        [
            "AWS",
        ],
        1,
        False,
    )
)

print(result)
