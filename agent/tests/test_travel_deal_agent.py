import os
import sys
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from agent.travel_deal_agent import evaluate_deals


def sample_params():
    return {
        "origin": "AAA",
        "destination": "BBB",
        "startDate": "2024-09-01",
        "nights": 5,
        "adults": 2,
        "children": 0,
        "minStars": 4,
        "board": "HB",
        "budgetPerPerson": 250,
    }


def test_evaluate_deals_filters_and_sorts():
    flights = [
        {"price": 100, "id": "F1"},
        {"price": 200, "id": "F2"},
    ]
    hotels = [
        {"name": "Hotel1", "stars": 5, "board": "HB", "price": 300},
        {"name": "Hotel2", "stars": 5, "board": "HB", "price": 500},
        {"name": "Hotel3", "stars": 3, "board": "HB", "price": 100},
        {"name": "Hotel4", "stars": 4, "board": "BB", "price": 100},
    ]

    with patch("agent.travel_deal_agent.get_kiwi_deals", return_value=flights) as mock_flights, \
         patch("agent.travel_deal_agent.get_amadeus_hotels", return_value=hotels) as mock_hotels:
        results = evaluate_deals(sample_params())

    mock_flights.assert_called_once()
    mock_hotels.assert_called_once()

    assert len(results) == 2
    per_person_prices = [deal["perPerson"] for deal in results]
    assert per_person_prices == sorted(per_person_prices)

    for deal in results:
        assert deal["hotel"]["stars"] >= 4
        assert "hb" in deal["hotel"]["board"].lower()
        assert deal["perPerson"] <= 250
        assert deal["hotel"]["name"] == "Hotel1"
