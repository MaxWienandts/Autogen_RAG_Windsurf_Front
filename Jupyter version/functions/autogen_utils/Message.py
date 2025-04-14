# Message

from dataclasses import dataclass

# This class is essential for Autogen, but additional attributes can be added if necessary.
@dataclass
class Message:
    content: str