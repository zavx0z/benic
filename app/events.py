from collections import defaultdict


class AsyncEventManager:
    def __init__(self):
        self.handlers = defaultdict(list)

    def subscribe(self, event_type, handler):
        self.handlers[event_type].append(handler)

    def unsubscribe(self, event_type, handler):
        if handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)

    async def notify(self, event_type, *args, **kwargs):
        for handler in self.handlers[event_type]:
            await handler(*args, **kwargs)
