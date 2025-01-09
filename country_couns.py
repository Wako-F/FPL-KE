import requests
import threading
import logging
import csv
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('fpl_national_league_fetch.log'), logging.StreamHandler()]
)

# Input and output CSV files
input_file = 'fpl_country_data.csv'
output_file = 'fpl_country_data_with_counts.csv'

# Function to fetch national league data
def fetch_national_league_data(entry_id):
    url = f"https://fantasy.premierleague.com/api/entry/{entry_id}/"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
        data = response.json()

        # Extract the national league's rank_count
        national_league = next(
            (league for league in data.get('leagues', {}).get('classic', []) if "region" in league.get('short_name', "")),
            None
        )

        if national_league:
            rank_count = national_league.get('rank_count', None)
            return rank_count
        else:
            logging.warning(f"No national league data found for Entry ID: {entry_id}")
            return None
    except Exception as e:
        logging.error(f"Error fetching Entry ID {entry_id}: {e}")
        return None

# Function to process each row and fetch national league player count
def process_row(row, results):
    entry_id = row['First Player Entry']
    rank_count = fetch_national_league_data(entry_id)
    if rank_count is not None:
        row['National League Player Count'] = rank_count
    else:
        row['National League Player Count'] = "N/A"
    results.append(row)

# Function to save results to CSV
def save_to_csv(data):
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = ['League ID', 'Country', 'First Player Entry', 'National League Player Count']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    logging.info(f"Data saved to {output_file}")

# Main function
def main():
    # Read the input CSV
    with open(input_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    threads = []
    results = []  # Shared results list
    lock = threading.Lock()  # Lock to prevent race conditions

    # Worker function to ensure thread safety
    def thread_worker(row):
        temp_results = []
        process_row(row, temp_results)
        with lock:
            results.extend(temp_results)

    # Create threads for each row
    for row in rows:
        thread = threading.Thread(target=thread_worker, args=(row,))
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # To avoid overwhelming the server

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Save results to CSV
    save_to_csv(results)

if __name__ == "__main__":
    main()
