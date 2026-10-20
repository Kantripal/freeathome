import pytest
pytestmark = pytest.mark.asyncio

import os
import logging
from async_mock import patch, AsyncMock

from fah.pfreeathome import Client
from common import load_fixture, init_client_state

LOG = logging.getLogger(__name__)

def get_client():
    client = Client()
    client.set_datapoint = AsyncMock()
    client._host = "localhost"
    client.component_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

    return client

@pytest.fixture(autouse=True)
def mock_init():
    with patch("fah.pfreeathome.Client.__init__", init_client_state):
        yield

@pytest.fixture(autouse=True)
def mock_roomnames():
    with patch("fah.pfreeathome.get_room_names", return_value={"00":{"00":"room1", "01":"room2"}}):
        yield

@patch("fah.pfreeathome.Client.get_config", return_value=load_fixture("1038_panel_door_call.xml"))
class TestDoorCall:
    async def test_door_call(self, _):
        client = get_client()
        await client.find_devices(True)

        devices = client.get_devices("binary_sensor")
        assert len(devices) == 2
        assert sorted(el.lookup_key for el in devices) == ["ABB7000A0001/ch0017", "ABB7000A0001/ch0018"]

        level_call = next((el for el in devices if el.lookup_key == "ABB7000A0001/ch0017"))
        assert level_call.name == "Etagenruftaster (room2)"

        # ch0018 has no displayName, floor and room, so the device values are used
        door_call = next((el for el in devices if el.lookup_key == "ABB7000A0001/ch0018"))
        assert door_call.name == 'free@homeTouch 7" [EG] (room2)'
        assert door_call.serialnumber == "ABB7000A0001"
        assert door_call.channel_id == "ch0018"
        assert door_call.device_info["identifiers"] == {("freeathome", "ABB7000A0001")}
        assert door_call.device_info["model"] == 'free@homeTouch 7"'
        # The initial value is taken over from the configuration (value 1 in the dump)
        assert door_call.state == '1'
        assert level_call.state == '1'

        # Test the door bell ringing
        callback = AsyncMock()
        door_call.register_datapoint_updated_cb(callback)

        await client.update_devices(load_fixture("1038_update_door_call.xml"))
        assert door_call.state == '1'

        callback.assert_awaited_once()
        device, event = callback.await_args.args
        assert device is door_call
        assert event["command"] == "pressed"
        assert event["state"] is True
