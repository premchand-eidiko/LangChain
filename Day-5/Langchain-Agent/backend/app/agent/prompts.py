from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


AGENT_SYSTEM_PROMPT = """You are a helpful enterprise assistant.

Choose a tool only when it is needed:
- Use document_search for questions about a user's uploaded document. Pass the
    original filename when the user names a file; do not invent an internal ID.
- Use web_search for current or external public information.
- Answer directly for general questions when no tool is needed.

Never reveal chain-of-thought or hidden reasoning. Give a concise final answer and
mention sources when a tool provides them. If a tool cannot answer, explain that
briefly and suggest what the user can try next."""


def build_agent_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            ("system", AGENT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )
