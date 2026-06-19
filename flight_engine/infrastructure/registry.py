from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class CollectorRegistry:
    def __init__(self):
        self._collectors: Dict[str, "BaseCollector"] = {}

    def register(self, collector: "BaseCollector") -> None:
        if collector.name in self._collectors:
            logger.warning(f"Collector {collector.name} is already registered. Overwriting.")
        self._collectors[collector.name] = collector
        logger.info(f"Registered collector: {collector.name}")

    def get_all(self) -> List["BaseCollector"]:
        return list(self._collectors.values())

    def get(self, name: str) -> "BaseCollector":
        return self._collectors[name]

registry = CollectorRegistry()
