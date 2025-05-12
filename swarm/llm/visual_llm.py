from abc import ABC, abstractmethod
from typing import Optional
from swarm.llm.llm import LLM


class VisualLLM(ABC):
    @abstractmethod
    def gen(self,
            task: Optional[str] = None,
            img: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def gen_video(self,
                  task: Optional[str] = None,
                  video: Optional[str] = None) -> str:
        pass
