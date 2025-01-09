import requests
import threading
import logging
import csv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('fpl_country_fetch.log'), logging.StreamHandler()]
)

# CSV output file
output_file = 'fpl_country_data.csv'

# Function to fetch league data
def fetch_league_data(league_id, results):
    url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        data = response.json()
        
        # Extract relevant details
        country_name = data.get('league', {}).get('name', f"Unknown-{league_id}")
        standings = data.get('standings', {}).get('results', [])
        
        if standings:
            first_player_entry = standings[0].get('entry', None)
            if first_player_entry:
                results.append({'League ID': league_id, 'Country': country_name, 'First Player Entry': first_player_entry})
                logging.info(f"Fetched: {country_name} (League ID: {league_id}, First Player Entry: {first_player_entry})")
        else:
            logging.warning(f"No standings data for League ID: {league_id}")
    except Exception as e:
        logging.error(f"Error fetching League ID {league_id}: {e}")

# Function to save results to CSV
def save_to_csv(data):
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['League ID', 'Country', 'First Player Entry'])
        writer.writeheader()
        writer.writerows(data)
    logging.info(f"Data saved to {output_file}")

# Main function
def main():
    threads = []
    results = []  # Shared results list
    lock = threading.Lock()  # Lock to prevent race conditions

    # Worker function to ensure thread safety
    def thread_worker(league_id):
        temp_results = []
        fetch_league_data(league_id, temp_results)
        with lock:
            results.extend(temp_results)

    # Create threads for each league ID
    for league_id in range(21, 276):  # League IDs from 21 to 275
        thread = threading.Thread(target=thread_worker, args=(league_id,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Save results to CSV
    save_to_csv(results)

if __name__ == "__main__":
    main()
