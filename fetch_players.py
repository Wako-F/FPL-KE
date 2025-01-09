import requests
import logging
import csv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("fetch_league.log"),
        logging.StreamHandler()
    ]
)

def fetch_league_page(league_id, page):
    """
    Fetch a specific page of league standings.
    """
    base_url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"
    try:
        response = requests.get(base_url, params={"page_standings": page})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching page {page} for league {league_id}: {e}")
        return None

def save_to_csv(file_name, data):
    """
    Save data to a CSV file incrementally.
    """
    file_exists = os.path.isfile(file_name)
    
    with open(file_name, mode='a', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        
        # Write header only if the file is new
        if not file_exists:
            writer.writerow([
                "player_id", "event_total", "player_name", 
                "rank", "last_rank", "total", "entry", "entry_name", "has_played"
            ])
        
        for player in data:
            writer.writerow([
                player["id"], player["event_total"], player["player_name"],
                player["rank"], player["last_rank"], player["total"],
                player["entry"], player["entry_name"], player["has_played"]
            ])

def fetch_and_save_all_players(league_id, file_name):
    """
    Fetch all players from the league and save incrementally to a CSV file.
    """
    page = 5063
    total_players = 0
    
    while True:
        logging.info(f"Fetching page {page} for league {league_id}...")
        data = fetch_league_page(league_id, page)
        
        if not data:
            logging.warning("No data returned. Stopping.")
            break
        
        standings = data.get("standings", {}).get("results", [])
        if not standings:
            logging.info("No more standings data found. Stopping.")
            break
        
        # Save to CSV
        save_to_csv(file_name, standings)
        total_players += len(standings)
        logging.info(f"Saved {len(standings)} players from page {page}. Total so far: {total_players}")
        
        # Check if there are more pages
        if not data.get("standings", {}).get("has_next", False):
            logging.info("Reached the last page of standings.")
            break
        
        page += 1

    logging.info(f"Finished fetching players. Total players fetched: {total_players}")

# Main execution
if __name__ == "__main__":
    league_id = 131  # Replace with your league ID
    output_file = "league_players.csv"
    fetch_and_save_all_players(league_id, output_file)
