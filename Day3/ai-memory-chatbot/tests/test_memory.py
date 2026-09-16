import unittest

from langchain_core.messages import AIMessage, HumanMessage

from app.memory import RedisMemory


class FakeRedis:
    def __init__(self):
        self.values = {}

    def ping(self):
        return True

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value):
        self.values[key] = value

    def expire(self, key, seconds):
        return True

    def delete(self, key):
        return int(self.values.pop(key, None) is not None)


class RedisMemoryTests(unittest.TestCase):
    def setUp(self):
        self.memory = RedisMemory("redis://unused")
        self.memory.client = FakeRedis()

    def test_messages_round_trip(self):
        messages = [
            HumanMessage(content="My name is Prem."),
            AIMessage(content="Nice to meet you, Prem."),
        ]

        self.memory.save("session-a", messages)

        loaded = self.memory.load("session-a")
        self.assertEqual([message.content for message in loaded], [
            "My name is Prem.",
            "Nice to meet you, Prem.",
        ])

    def test_sessions_are_isolated(self):
        self.memory.save("session-a", [HumanMessage(content="Prem")])
        self.memory.save("session-b", [HumanMessage(content="Another user")])

        self.assertEqual(self.memory.load("session-a")[0].content, "Prem")
        self.assertEqual(self.memory.load("session-b")[0].content, "Another user")

    def test_clear_removes_session(self):
        self.memory.save("session-a", [HumanMessage(content="temporary")])

        self.assertTrue(self.memory.clear("session-a"))
        self.assertEqual(self.memory.load("session-a"), [])


if __name__ == "__main__":
    unittest.main()