import asyncio
import time

from starburst.event_sources.base_event_source import BaseEventSource
from starburst.types.events import SchedTick


class SchedTickEventSource(BaseEventSource):
    """A periodic tick event source."""

    def __init__(self, output_queue, timeout_time, sleep_time=None):
        """Constructor."""
        self.timeout_time = timeout_time
        self.sleep_time = sleep_time if sleep_time else timeout_time / 3
        self.last_alloc_or_event_gen_time = time.time() - self.timeout_time
        super().__init__(output_queue)

    async def event_generator(self):
        """Generates the event."""
        while True:
            curr_time = time.time()
            if curr_time >= self.last_alloc_or_event_gen_time \
               + self.timeout_time:
                event = SchedTick(timestamp=curr_time)
                self.last_alloc_or_event_gen_time = curr_time
                await self.output_queue.put(event)
            await asyncio.sleep(self.sleep_time)
