from uuid import uuid4

from langchain_core.language_models.fake_chat_models import FakeListChatModel

from app.agent.agent import build_agent_executor, build_agent_tools
from app.agent.prompts import AGENT_SYSTEM_PROMPT


class ToolBindingFakeChatModel(FakeListChatModel):
    def bind_tools(self, tools, **kwargs):
        object.__setattr__(self, "bound_tools", tools)
        return self


def test_agent_exposes_document_and_web_tools():
    model = ToolBindingFakeChatModel(responses=["Direct answer about APIs."])
    executor = build_agent_executor(None, uuid4(), llm=model)

    assert [tool.name for tool in executor.tools] == [
        "document_search",
        "web_search",
    ]
    assert len(model.bound_tools) == 2


def test_agent_can_return_a_direct_answer_without_tool():
    model = ToolBindingFakeChatModel(responses=["An API is a way for programs to communicate."])
    executor = build_agent_executor(None, uuid4(), llm=model)

    result = executor.invoke({"input": "What is an API?"})

    assert result["output"] == "An API is a way for programs to communicate."
    assert "chain-of-thought" in AGENT_SYSTEM_PROMPT
