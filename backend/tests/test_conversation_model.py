from __future__ import annotations

from eval_server.models.conversation import Conversation, ToolCall, Turn


def test_build_conversation_with_and_without_tool_calls():
    conv = Conversation(version="1.0.0", conversation_id="conv-1")
    conv.add_turn("user", "Search for leave policy", tool_call=ToolCall(tool_name="doc_search", arguments={"q": "leave policy"}))
    conv.add_turn("assistant", "Found policy: 25 days")

    assert len(conv.turns) == 2
    assert conv.turns[0].turn_id == "t1"
    assert conv.turns[1].turn_id == "t2"
    assert conv.turns[0].tool_call is not None
    assert conv.turns[0].tool_call.tool_name == "doc_search"
    assert conv.turns[1].tool_call is None

    user_turns = list(conv.iter_user())
    assistant_turns = list(conv.iter_assistant())
    assert len(user_turns) == 1 and user_turns[0].content.startswith("Search")
    assert len(assistant_turns) == 1 and assistant_turns[0].content.startswith("Found")


def test_from_dict_legacy_compatibility():
    legacy = {
        "version": "1.0.0",
        "conversation_id": "x",
        "turns": [
            {"turn_id": "t1", "role": "user", "content": "Hi", "tool_calls": [{"tool_name": "tool", "arguments": {"a": 1}}]},
            {"turn_id": "t2", "role": "assistant", "content": "Hello"}
        ]
    }
    conv = Conversation.from_dict(legacy)
    assert conv.turns[0].speaker == "user"
    assert conv.turns[0].tool_call is not None
    assert conv.turns[1].speaker == "assistant"
