from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    async def fetch(self, client, keyword):
        pass
