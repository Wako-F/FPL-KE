import pandas as pd
import numpy as np

# Load the data
file_name = "league_players.csv"
output_file = "cleaned_league_players.csv"

# Load the CSV file
print("Loading data...")
df = pd.read_csv(file_name)

# Display initial summary
print("Initial dataset info:")
print(df.info())
print(df.describe())

# Step 1: Handle Missing Values
print("Handling missing values...")
# Fill missing numerical values with 0 or mean (depending on context)
numerical_columns = ["event_total", "rank", "last_rank", "total", "years_active", "summary_overall_rank"]
df[numerical_columns] = df[numerical_columns].fillna(0)

# Fill missing string values with "Unknown"
string_columns = ["player_name", "entry_name", "joined_time", "favourite_team"]
df[string_columns] = df[string_columns].fillna("Unknown")

# Step 2: Correct Data Types
print("Correcting data types...")
# Convert joined_time to datetime
df["joined_time"] = pd.to_datetime(df["joined_time"], errors="coerce")

# Convert categorical data to category type
categorical_columns = ["player_name", "entry_name", "favourite_team", "has_played"]
for col in categorical_columns:
    df[col] = df[col].astype("category")

# Convert numerical columns to appropriate types
integer_columns = ["rank", "last_rank", "years_active", "summary_overall_rank", "event_total", "total", "started_event", "player_id", "entry"]
for col in integer_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

# Step 3: Handle Duplicates
print("Removing duplicates...")
df = df.drop_duplicates(subset="player_id")

# # Step 4: Standardize Text
# print("Standardizing text fields...")
# # Strip whitespace and make lowercase for text fields
# text_columns = ["player_name", "entry_name", "favourite_team"]
# for col in text_columns:
#     df[col] = df[col].str.strip().str.lower()

# # Step 5: Remove Outliers (Optional)
# print("Handling outliers...")
# # Example: Remove players with impossible ranks
# df = df[df["rank"] > 0]

# Step 6: Validate Data
print("Validating data...")
# Check for missing or invalid datetime values
invalid_dates = df["joined_time"].isnull().sum()
print(f"Invalid dates: {invalid_dates}")

# Step 7: Save Cleaned Data
print("Saving cleaned data...")
df.to_csv(output_file, index=False)

print("Data cleaning complete. Cleaned file saved as:", output_file)
