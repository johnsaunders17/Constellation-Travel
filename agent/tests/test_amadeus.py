import os
import sys
from unittest.mock import Mock, patch
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from agent.providers.amadeus import get_amadeus_hotels, get_amadeus_access_token


def sample_params():
  return {
      "startDate": "2024-09-01",
      "nights": 3,
      "adults": 2,
  }


def mock_token_response():
  resp = Mock()
  resp.raise_for_status = Mock()
  resp.json.return_value = {"access_token": "token"}
  return resp


def test_get_amadeus_hotels_success():
  os.environ["AMADEUS_API_KEY"] = "key"
  os.environ["AMADEUS_API_SECRET"] = "secret"
  hotel_resp = Mock()
  hotel_resp.raise_for_status = Mock()
  hotel_resp.json.return_value = {
      "data": [
          {
              "hotel": {"name": "Hotel"},
              "offers": [{"boardType": "BB", "price": {"total": "50"}}]
          }
      ]
  }
  with patch("agent.providers.amadeus.requests.post", return_value=mock_token_response()), \
       patch("agent.providers.amadeus.requests.get", return_value=hotel_resp):
      results = get_amadeus_hotels(sample_params())
  assert results[0]["name"] == "Hotel"


def test_get_amadeus_hotels_error():
  os.environ["AMADEUS_API_KEY"] = "key"
  os.environ["AMADEUS_API_SECRET"] = "secret"
  with patch("agent.providers.amadeus.requests.post", return_value=mock_token_response()), \
       patch("agent.providers.amadeus.requests.get", side_effect=Exception("boom")):
      results = get_amadeus_hotels(sample_params())
  assert results == []


def test_get_amadeus_access_token_missing_key():
  os.environ.pop("AMADEUS_API_KEY", None)
  os.environ.pop("AMADEUS_API_SECRET", None)
  with pytest.raises(RuntimeError):
      get_amadeus_access_token()
