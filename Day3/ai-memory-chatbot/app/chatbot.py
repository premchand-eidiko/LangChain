from typing import List

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq

from .config import Settings
from .memory import RedisMemory


class Chatbot:
	def __init__(self, settings: Settings, memory: RedisMemory) -> None:
		self.memory = memory
		self.model = ChatGroq(
			api_key=settings.groq_api_key,
			model=settings.groq_model,
			temperature=0,
		)

	def reply(self, session_id: str, user_message: str) -> str:
		history: List[BaseMessage] = self.memory.load(session_id)
		messages = history + [HumanMessage(content=user_message)]
		response = self.model.invoke(messages)
		response_text = str(response.content)
		self.memory.save(
			session_id,
			messages + [response],
		)
		return response_text
