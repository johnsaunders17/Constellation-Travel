import os
import sys
from unittest.mock import Mock, patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from agent.providers.kiwi import get_kiwi_deals


def sample_params():
  return {
      "origin": "EMA",
      "destination": "ALC",
      "startDate": "2024-09-01",
      "nights": 3,
      "adults": 2,
      "children": 0,
  }


def test_get_kiwi_deals_success():
  os.environ["RAPIDAPI_KIWI_KEY"] = "dummy"
  mock_resp = Mock()
  mock_resp.raise_for_status = Mock()
  mock_resp.json.return_value = {
      "data": [
          {
              "price": 100,
              "airlines": ["XY"],
              "route": [{"local_departure": "2024-09-01T10:00"}, {"local_arrival": "2024-09-01T12:00"}],
              "deep_link": "link"
          }
      ]
  }
  with patch("agent.providers.kiwi.requests.get", return_value=mock_resp) as mock_get:
      deals = get_kiwi_deals(sample_params())
  assert deals[0]["price"] == 100
  mock_get.assert_called_once()
  called_url = mock_get.call_args[0][0]
  called_headers = mock_get.call_args[1]["headers"]
  called_params = mock_get.call_args[1]["params"]
  assert called_url == "https://kiwi-com.p.rapidapi.com/v2/search"
  assert called_headers["X-RapidAPI-Host"] == "kiwi-com.p.rapidapi.com"
  assert called_params["date_from"] == "01/09/2024"
  assert called_params["date_to"] == "01/09/2024"


def test_get_kiwi_deals_error():
  os.environ["RAPIDAPI_KIWI_KEY"] = "dummy"
  with patch("agent.providers.kiwi.requests.get", side_effect=Exception("boom")):
      deals = get_kiwi_deals(sample_params())
  assert deals == []


def test_get_kiwi_deals_missing_key():
  os.environ.pop("RAPIDAPI_KIWI_KEY", None)
  with pytest.raises(RuntimeError):
      get_kiwi_deals(sample_params())
