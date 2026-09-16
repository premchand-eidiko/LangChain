import json
from typing import List

import redis
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


class RedisMemory:
	"""Store one conversation buffer per session in Redis."""

	def __init__(self, redis_url: str, ttl_seconds: int = 0) -> None:
		self.client = redis.Redis.from_url(redis_url, decode_responses=True)
		self.ttl_seconds = ttl_seconds

	@staticmethod
	def _key(session_id: str) -> str:
		return "conversation:" + session_id

	def ping(self) -> bool:
		return bool(self.client.ping())

	def load(self, session_id: str) -> List[BaseMessage]:
		stored_messages = self.client.get(self._key(session_id))
		if not stored_messages:
			return []

		messages = []
		for item in json.loads(stored_messages):
			if item["role"] == "user":
				messages.append(HumanMessage(content=item["content"]))
			elif item["role"] == "assistant":
				messages.append(AIMessage(content=item["content"]))
		return messages

	def save(self, session_id: str, messages: List[BaseMessage]) -> None:
		serialized = []
		for message in messages:
			if isinstance(message, HumanMessage):
				role = "user"
			elif isinstance(message, AIMessage):
				role = "assistant"
			else:
				continue
			serialized.append({"role": role, "content": message.content})

		key = self._key(session_id)
		self.client.set(key, json.dumps(serialized))
		if self.ttl_seconds > 0:
			self.client.expire(key, self.ttl_seconds)

	def inspect(self, session_id: str) -> List[dict]:
		stored_messages = self.client.get(self._key(session_id))
		return json.loads(stored_messages) if stored_messages else []

	def clear(self, session_id: str) -> bool:
		return bool(self.client.delete(self._key(session_id)))
