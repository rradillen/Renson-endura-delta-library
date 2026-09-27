import json
from datetime import datetime
from unittest.mock import patch

import requests_mock

from renson_endura_delta.general_enum import Level
import pytest

from renson_endura_delta.general_enum import ServiceNames
from renson_endura_delta.renson import RensonVentilation as Services

SERVICE_SUFFIX = "?index0=0&index1=0&index2=0"


def get_service_url(field):
    return "http://example.mock/JSON/Vars/" + field.replace(" ", "%20") + SERVICE_SUFFIX


def assert_json_request(request, url, value):
    assert request.method == "POST"
    assert request.url == url
    assert json.loads(request.text) == {"Value": value}


def test_set_manual_level():
    with requests_mock.Mocker() as m:
        m.post(get_service_url(ServiceNames.SET_MANUAL_LEVEL_FIELD.value),
               text='ok')

        service = Services("example.mock")
        service.set_manual_level(Level.LEVEL2)

        assert_json_request(
            m.request_history[0],
            get_service_url(ServiceNames.SET_MANUAL_LEVEL_FIELD.value),
            Level.LEVEL2.value,
        )


def test_set_filter_days():
    with requests_mock.Mocker() as m:
        m.post(get_service_url(ServiceNames.FILTER_DAYS_FIELD.value),
               text="{'Value'='30'}")

        service = Services("example.mock")
        service.set_filter_days(30)

        assert_json_request(
            m.request_history[0],
            get_service_url(ServiceNames.FILTER_DAYS_FIELD.value),
            "30",
        )


def test_private_url_helpers():
    service = Services("example.mock")

    assert service._RensonVentilation__get_service_url(
        ServiceNames.SET_MANUAL_LEVEL_FIELD
    ) == get_service_url(ServiceNames.SET_MANUAL_LEVEL_FIELD.value)
    assert service._RensonVentilation__get_base_url("/Reset") == "http://example.mock/Reset"


def test_set_remaining_filter_days():
    with requests_mock.Mocker() as m:
        m.post(get_service_url(ServiceNames.FILTER_REMAIN_FIELD.value), text="ok")

        service = Services("example.mock")
        service.set_remaining_filter_days(149)

        assert_json_request(
            m.request_history[0],
            get_service_url(ServiceNames.FILTER_REMAIN_FIELD.value),
            "149",
        )


def test_set_timer_level():
    with requests_mock.Mocker() as m:
        m.post(get_service_url(ServiceNames.TIMER_FIELD.value), text="ok")

        service = Services("example.mock")
        service.set_timer_level(Level.LEVEL4, 30)

        assert_json_request(
            m.request_history[0],
            get_service_url(ServiceNames.TIMER_FIELD.value),
            "30 min Level4",
        )


def test_set_timer_level_rejects_off():
    service = Services("example.mock")

    with pytest.raises(Exception, match="Off is not a valid type"):
        service.set_timer_level(Level.OFF, 30)


def test_set_breeze():
    with requests_mock.Mocker() as m:
        m.post(get_service_url(ServiceNames.BREEZE_LEVEL_FIELD.value), text="ok")
        m.post(get_service_url(ServiceNames.BREEZE_TEMPERATURE_FIELD.value), text="ok")
        m.post(get_service_url(ServiceNames.BREEZE_ENABLE_FIELD.value), text="ok")

        service = Services("example.mock")
        service.set_breeze(Level.LEVEL3, 20, True)

        assert len(m.request_history) == 3
        assert_json_request(
            m.request_history[0],
            get_service_url(ServiceNames.BREEZE_LEVEL_FIELD.value),
            Level.LEVEL3.value,
        )
        assert_json_request(
            m.request_history[1],
            get_service_url(ServiceNames.BREEZE_TEMPERATURE_FIELD.value),
            "20",
        )
        assert_json_request(
            m.request_history[2],
            get_service_url(ServiceNames.BREEZE_ENABLE_FIELD.value),
            "1",
        )


@pytest.mark.parametrize("level", [Level.OFF, Level.HOLIDAY, Level.BREEZE])
def test_set_breeze_rejects_invalid_levels(level):
    service = Services("example.mock")

    with pytest.raises(Exception, match="Holiday, Off, Breeze are not a valid types"):
        service.set_breeze(level, 20, True)


def test_set_day_time():
    with requests_mock.Mocker() as m:
        m.post(get_service_url(ServiceNames.DAYTIME_FIELD.value), text="ok")

        service = Services("example.mock")
        service.set_day_time("07:00")

        assert_json_request(
            m.request_history[0],
            get_service_url(ServiceNames.DAYTIME_FIELD.value),
            "07:00",
        )


def test_set_night_time():
    with requests_mock.Mocker() as m:
        m.post(get_service_url(ServiceNames.NIGHTTIME_FIELD.value), text="ok")

        service = Services("example.mock")
        service.set_night_time("21:30")

        assert_json_request(
            m.request_history[0],
            get_service_url(ServiceNames.NIGHTTIME_FIELD.value),
            "21:30",
        )


def test_restart_device():
    with requests_mock.Mocker() as m:
        m.post("http://example.mock/Reset", text="ok")

        service = Services("example.mock")
        service.restart_device()

        request = m.request_history[0]
        assert request.method == "POST"
        assert request.url == "http://example.mock/Reset"


def test_set_pollution():
    with requests_mock.Mocker() as m:
        m.post(get_service_url(ServiceNames.DAY_POLLUTION_FIELD.value), text="ok")
        m.post(get_service_url(ServiceNames.NIGHT_POLLUTION_FIELD.value), text="ok")
        m.post(get_service_url(ServiceNames.HUMIDITY_CONTROL_FIELD.value), text="ok")
        m.post(get_service_url(ServiceNames.AIR_QUALITY_CONTROL_FIELD.value), text="ok")
        m.post(get_service_url(ServiceNames.CO2_CONTROL_FIELD.value), text="ok")
        m.post(get_service_url(ServiceNames.CO2_THRESHOLD_FIELD.value), text="ok")
        m.post(get_service_url(ServiceNames.CO2_HYSTERESIS_FIELD.value), text="ok")

        service = Services("example.mock")
        service.set_pollution(Level.LEVEL3, Level.LEVEL2, True, False, True, 600, 100)

        assert len(m.request_history) == 7
        assert_json_request(
            m.request_history[0],
            get_service_url(ServiceNames.DAY_POLLUTION_FIELD.value),
            Level.LEVEL3.value,
        )
        assert_json_request(
            m.request_history[1],
            get_service_url(ServiceNames.NIGHT_POLLUTION_FIELD.value),
            Level.LEVEL2.value,
        )
        assert_json_request(
            m.request_history[2],
            get_service_url(ServiceNames.HUMIDITY_CONTROL_FIELD.value),
            "1",
        )
        assert_json_request(
            m.request_history[3],
            get_service_url(ServiceNames.AIR_QUALITY_CONTROL_FIELD.value),
            "0",
        )
        assert_json_request(
            m.request_history[4],
            get_service_url(ServiceNames.CO2_CONTROL_FIELD.value),
            "1",
        )
        assert_json_request(
            m.request_history[5],
            get_service_url(ServiceNames.CO2_THRESHOLD_FIELD.value),
            "600",
        )
        assert_json_request(
            m.request_history[6],
            get_service_url(ServiceNames.CO2_HYSTERESIS_FIELD.value),
            "100",
        )


@pytest.mark.parametrize("day,night,error", [
    (Level.OFF, Level.LEVEL2, "day level"),
    (Level.HOLIDAY, Level.LEVEL2, "day level"),
    (Level.BREEZE, Level.LEVEL2, "day level"),
    (Level.LEVEL2, Level.OFF, "night level"),
    (Level.LEVEL2, Level.HOLIDAY, "night level"),
    (Level.LEVEL2, Level.BREEZE, "night level"),
])
def test_set_pollution_rejects_invalid_levels(day, night, error):
    service = Services("example.mock")

    with pytest.raises(Exception, match=error):
        service.set_pollution(day, night, True, True, True, 600, 100)


def test_sync_time_without_update():
    with requests_mock.Mocker() as m:
        m.get(
            get_service_url(ServiceNames.TIME_AND_DATE_FIELD.value),
            json={"Value": "22 Aug 2021 13:12"},
        )

        fixed_time = datetime(2021, 8, 22, 13, 12)
        service = Services("example.mock")

        with patch("renson_endura_delta.renson.datetime") as mock_datetime:
            mock_datetime.strptime.return_value = fixed_time
            mock_datetime.now.return_value = fixed_time

            service.sync_time()

        assert len(m.request_history) == 1
        assert m.request_history[0].method == "GET"
        assert m.request_history[0].url == get_service_url(ServiceNames.TIME_AND_DATE_FIELD.value)


def test_sync_time_with_update():
    with requests_mock.Mocker() as m:
        m.get(
            get_service_url(ServiceNames.TIME_AND_DATE_FIELD.value),
            json={"Value": "22 Aug 2021 13:12"},
        )
        m.post(get_service_url(ServiceNames.TIME_AND_DATE_FIELD.value), text="ok")

        device_time = datetime(2021, 8, 22, 13, 12)
        current_time = datetime(2021, 8, 22, 13, 13)
        service = Services("example.mock")

        with patch("renson_endura_delta.renson.datetime") as mock_datetime:
            mock_datetime.strptime.return_value = device_time
            mock_datetime.now.return_value = current_time

            service.sync_time()

        assert len(m.request_history) == 2
        assert m.request_history[0].method == "GET"
        assert m.request_history[0].url == get_service_url(ServiceNames.TIME_AND_DATE_FIELD.value)
        assert_json_request(
            m.request_history[1],
            get_service_url(ServiceNames.TIME_AND_DATE_FIELD.value),
            "22 aug 2021 13:13",
        )


def test_sync_time_non_200():
    with requests_mock.Mocker() as m:
        m.get(get_service_url(ServiceNames.TIME_AND_DATE_FIELD.value), status_code=500)

        service = Services("example.mock")
        service.sync_time()

        assert len(m.request_history) == 1
        assert m.request_history[0].method == "GET"
        assert m.request_history[0].url == get_service_url(ServiceNames.TIME_AND_DATE_FIELD.value)


def test_is_firmware_up_to_date():
    with requests_mock.Mocker() as m:
        m.post(
            Services.firmware_server_url,
            json={"latest": True},
        )

        service = Services("example.mock")

        assert service.is_firmware_up_to_date("Endura Delta 0.0.67")
        assert len(m.request_history) == 1
        assert m.request_history[0].url == Services.firmware_server_url
        assert m.request_history[0].text == '{"a":"check", "name":"D_0.0.67.fuf"}'


def test_is_firmware_up_to_date_non_200():
    with requests_mock.Mocker() as m:
        m.post(Services.firmware_server_url, status_code=503)

        service = Services("example.mock")

        assert not service.is_firmware_up_to_date("Endura Delta 0.0.67")
        assert len(m.request_history) == 1
        assert m.request_history[0].url == Services.firmware_server_url
        assert m.request_history[0].text == '{"a":"check", "name":"D_0.0.67.fuf"}'


def test_get_latest_firmware_version():
    with requests_mock.Mocker() as m:
        m.post(Services.firmware_server_url, json={"url": "D_1.2.3.fuf"})

        service = Services("example.mock")

        assert service.get_latest_firmware_version() == "1.2.3"
        assert len(m.request_history) == 1
        assert m.request_history[0].url == Services.firmware_server_url
        assert m.request_history[0].text == '{"a":"check", "name":"D_0.fuf"}'


def test_get_latest_firmware_version_non_200():
    with requests_mock.Mocker() as m:
        m.post(Services.firmware_server_url, status_code=503)

        service = Services("example.mock")

        assert service.get_latest_firmware_version() == ""
        assert len(m.request_history) == 1
        assert m.request_history[0].url == Services.firmware_server_url
        assert m.request_history[0].text == '{"a":"check", "name":"D_0.fuf"}'


def test_reset_filter():
    service = Services("example.mock")
    data = {"ModifiedItems": [{"Name": "Filter preset time", "Value": "180"}]}

    with patch.object(service, "get_all_data", return_value=data) as mock_get_all_data:
        with patch.object(service, "set_remaining_filter_days") as mock_set_remaining_filter_days:
            service.reset_filter()

    mock_get_all_data.assert_called_once_with()
    mock_set_remaining_filter_days.assert_called_once_with(180)
