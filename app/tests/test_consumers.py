from channels.testing import WebsocketCommunicator
from django.test import AsyncTestCase
from chat.app.consumers import MyConsumer

class MyConsumerTests(AsyncTestCase):
    async def test_connection(self):
        communicator = WebsocketCommunicator(MyConsumer.as_asgi(), "/ws/some_path/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

    async def test_message(self):
        communicator = WebsocketCommunicator(MyConsumer.as_asgi(), "/ws/some_path/")
        await communicator.connect()
        await communicator.send_to(text_data="Hello, World!")
        response = await communicator.receive_from()
        self.assertEqual(response, "Hello, World!")