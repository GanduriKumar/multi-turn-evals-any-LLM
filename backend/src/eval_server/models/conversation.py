from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Iterator, List, Literal, Optional


Speaker = Literal["user", "assistant"]


@dataclass
class ToolCall:
    tool_name: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    result: Any | None = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"tool_name": self.tool_name}
        if self.arguments:
            data["arguments"] = self.arguments
        if self.result is not None:
            data["result"] = self.result
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ToolCall":
        return ToolCall(
            tool_name=str(data["tool_name"]),
            arguments=dict(data.get("arguments", {})),
            result=data.get("result"),
        )


@dataclass
class Turn:
    turn_id: str
    speaker: Speaker
    content: str
    tool_call: Optional[ToolCall] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "turn_id": self.turn_id,
            "speaker": self.speaker,
            "content": self.content,
        }
        if self.tool_call is not None:
            out["tool_call"] = self.tool_call.to_dict()
        return out

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Turn":
        # Support legacy 'role'
        speaker = data.get("speaker") or data.get("role")
        if speaker not in ("user", "assistant"):
            raise ValueError("turn speaker/role must be 'user' or 'assistant'")
        tc = data.get("tool_call")
        if tc is None and isinstance(data.get("tool_calls"), list) and data["tool_calls"]:
            # If legacy array exists, take the first one for modeling convenience
            tc = data["tool_calls"][0]
        tool = ToolCall.from_dict(tc) if isinstance(tc, dict) else None
        return Turn(
            turn_id=str(data["turn_id"]),
            speaker=speaker,  # type: ignore[arg-type]
            content=str(data["content"]),
            tool_call=tool,
        )


@dataclass
class Conversation:
    version: str
    conversation_id: str
    turns: List[Turn] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_turn(self, speaker: Speaker, content: str, *, turn_id: str | None = None, tool_call: ToolCall | None = None) -> Turn:
        if turn_id is None:
            turn_id = f"t{len(self.turns) + 1}"
        turn = Turn(turn_id=turn_id, speaker=speaker, content=content, tool_call=tool_call)
        self.turns.append(turn)
        return turn

    def iter_user(self) -> Iterator[Turn]:
        return (t for t in self.turns if t.speaker == "user")

    def iter_assistant(self) -> Iterator[Turn]:
        return (t for t in self.turns if t.speaker == "assistant")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "conversation_id": self.conversation_id,
            "metadata": self.metadata,
            "turns": [t.to_dict() for t in self.turns],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Conversation":
        turns = [Turn.from_dict(d) for d in data.get("turns", [])]
        return Conversation(
            version=str(data.get("version", "1.0.0")),
            conversation_id=str(data["conversation_id"]),
            metadata=dict(data.get("metadata", {})),
            turns=turns,
        )
