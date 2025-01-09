import pandas as pd
import requests
import logging
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("update_players.log"),
        logging.StreamHandler()
    ]
)

# Constants
CHECKPOINT_FILE = "processed_ids.txt"
THREADS = 10  # Number of threads for parallel API calls

# Function to fetch manager data with retries
def fetch_manager_data(manager_id, max_retries=3):
    url = f"https://fantasy.premierleague.com/api/entry/{manager_id}/"
    retries = 0
    backoff = 1

    while retries < max_retries:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            retries += 1
            logging.warning(f"Retry {retries}/{max_retries} for manager_id {manager_id}: {e}")
            time.sleep(backoff)
            backoff *= 2  # Exponential backoff

    logging.error(f"Failed to fetch data for manager_id {manager_id} after {max_retries} retries.")
    return None

# Save checkpoint of processed IDs
def save_checkpoint(processed_ids):
    with open(CHECKPOINT_FILE, "w") as f:
        f.write("\n".join(map(str, processed_ids)))

# Load checkpoint
def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return set(map(int, f.read().splitlines()))
    return set()

# Update the DataFrame with fetched data
def update_player_data(row, processed_ids):
    manager_id = row["entry"]
    if manager_id in processed_ids:
        return None  # Skip already processed IDs

    data = fetch_manager_data(manager_id)
    if data:
        return {
            "index": row.name,
            "joined_time": data.get("joined_time"),
            "started_event": data.get("started_event"),
            "favourite_team": data.get("favourite_team"),
            "years_active": data.get("years_active"),
            "summary_overall_rank": data.get("summary_overall_rank"),
        }
    return None

# Parallel data fetching
def process_data_in_parallel(df, processed_ids):
    updates = []
    with ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(update_player_data, row, processed_ids): row for _, row in df.iterrows()}
        for future in as_completed(futures):
            result = future.result()
            if result:
                updates.append(result)
    return updates

# Main function to update CSV
def update_csv(file_path):
    # Load the CSV
    df = pd.read_csv(file_path)
    
    # Add columns if not already present
    for col in ["joined_time","started_event", "favourite_team", "years_active", "summary_overall_rank"]:
        if col not in df.columns:
            df[col] = None

    # Load processed IDs
    processed_ids = load_checkpoint()
    logging.info(f"Loaded {len(processed_ids)} processed IDs from checkpoint.")

    # Process data in batches
    batch_size = 1000
    for start in range(0, len(df), batch_size):
        batch_df = df.iloc[start:start + batch_size]
        logging.info(f"Processing batch {start // batch_size + 1}: rows {start} to {start + len(batch_df) - 1}")

        # Fetch data in parallel
        updates = process_data_in_parallel(batch_df, processed_ids)

        # Apply updates to the DataFrame
        for update in updates:
            df.at[update["index"], "joined_time"] = update["joined_time"]
            df.at[update["index"], "started_event"] = update["started_event"]
            df.at[update["index"], "favourite_team"] = update["favourite_team"]
            df.at[update["index"], "years_active"] = update["years_active"]
            df.at[update["index"], "summary_overall_rank"] = update["summary_overall_rank"]

            # Add to processed IDs
            processed_ids.add(df.at[update["index"], "entry"])

        # Save progress
        df.to_csv(file_path, index=False)
        save_checkpoint(processed_ids)
        logging.info(f"Batch {start // batch_size + 1} processed and saved.")

    logging.info("All updates completed.")

# Main execution
if __name__ == "__main__":
    csv_file_path = "league_players.csv"  # Path to your CSV file
    update_csv(csv_file_path)
