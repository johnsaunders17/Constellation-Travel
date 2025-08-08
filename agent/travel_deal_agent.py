import os
import json
import argparse
from datetime import datetime
from providers.kiwi import get_kiwi_deals
from providers.amadeus import get_amadeus_hotels

def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_results(data, output_dir="results"):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    output_file = f"{output_dir}/results-{timestamp}.json"
    latest_file = f"{output_dir}/latest.json"

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    with open(latest_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"[INFO] Results saved to {output_file} and latest.json")

def evaluate_deals(params):
    print("[INFO] Fetching flight data via Kiwi...")
    flights = get_kiwi_deals(params)
    print(f"[INFO] Found {len(flights)} flight options.")

    print("[INFO] Fetching hotel data via Amadeus...")
    hotels = get_amadeus_hotels(params)
    print(f"[INFO] Found {len(hotels)} hotel options.")

    results = []
    for flight in flights:
        for hotel in hotels:
            if hotel["stars"] >= params["minStars"] and params["board"].lower() in hotel["board"].lower():
                total = float(flight["price"]) + float(hotel["price"])
                per_person = total / params["adults"]
                if per_person <= params["budgetPerPerson"]:
                    results.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "perPerson": round(per_person, 2),
                        "total": round(total, 2),
                        "flight": flight,
                        "hotel": hotel
                    })

    sorted_results = sorted(results, key=lambda x: x["perPerson"])
    print(f"[INFO] {len(sorted_results)} matching deals found.")
    return sorted_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/request.json", help="Path to config JSON")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"[ERROR] Config file not found at {args.config}")
        exit(1)

    config = load_config(args.config)
    try:
        deals = evaluate_deals(config)
        output = {"deals": deals, "count": len(deals), "queriedAt": datetime.utcnow().isoformat()}
        save_results(output)
    except Exception as e:
        print(f"[ERROR] Agent failed: {e}")
        exit(1)
