"""" Core Test """
import asyncio
from triton_telemetry import core



#asyncio.run(main())

result = asyncio.run(core.scan_all_providers(
        [
            "AWS",
            "Azure",
            "GCP",
        ],
        1,
        True,
    )
)

print(result)
