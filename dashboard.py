import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

# Set page configuration
st.set_page_config(page_title="League Dashboard", layout="centered")

# Load the data
DATA_FILE = "cleaned_league_players.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)

df = load_data()
# Title
st.title("FPL Kenya")
# Overview Tab
tab1, tab2, tab3 = st.tabs(["Overview", "Leaderboards", "Search"])

with tab1:
    
    
    # Main Summary
    total_players = df.shape[0]
    avg_points = df["total"].mean()
    gw20_avg = df["event_total"].mean()
    years_active = df["years_active"].mean()
    st.caption("General Overview")
     # Custom CSS for responsive and aligned metrics
    st.markdown(
        """
        <style>
        /* Responsive container for metrics */
        .metrics-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-box {
            
            border-radius: 10px;
            padding: 15px 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            font-family: Arial, sans-serif;
        }
        .metric-box h3 {
            margin: 0;
            font-size: 18px;
            
        }
        .metric-box p {
            margin: 0;
            font-size: 24px;
            font-weight: bold;
            
        }
        /* Adjust layout for smaller screens */
        @media (max-width: 768px) {
            .metrics-container {
                flex-direction: column;
            }
            .metric-box {
                width: 100%;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # HTML structure for metrics
    st.markdown(
        f"""
        <div class="metrics-container">
            <div class="metric-box">
                <h3>Total Players</h3>
                <p>{total_players:,}</p>
            </div>
            <div class="metric-box">
                <h3>Avg. Total Points</h3>
                <p>{avg_points:.2f}</p>
            </div>
            <div class="metric-box">
                <h3>GW20 Avg.</h3>
                <p>{gw20_avg:.2f}</p>
            </div>
            <div class="metric-box">
                <h3>Avg. Years Active</h3>
                <p>{years_active:.1f}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Metric Cards in a grid
    # col1, col2, col3, col4 = st.columns(4)
    # with col1:
    #     st.metric("Total Players", f"{total_players:,}", help="Total number of Kenyan FPL managers.")
    # with col2:
    #     st.metric("Average Points", f"{avg_points:.2f}", help="The average total points of Kenyan managers.")
    # with col3:
    #     st.metric("GW 20 Avg", f"{gw20_avg:.2f}", help="Average GW 20 points of Kenyan managers.")
    # with col4:
    #     st.metric("Years Active (Avg)", f"{df['years_active'].mean():.1f}", help="Average years active per player.")

    # Add some spacing
    st.markdown("---")

    # Create the histogram for distribution of total points
    fig = px.histogram(
        df,
        x="total",
        nbins=50,  # Number of bins for better granularity
        title="Distribution of Total Points",
        labels={"total": "Total Points", "count": "Number of Players"},
        template="plotly_dark",
        color_discrete_sequence=["royalblue"],  # Aesthetic bar color
    )

    # Customize the layout
    fig.update_layout(
        title=dict(
            text="Distribution of Total Points",
            # x=0.5,  # Center the title
            font=dict(size=20)
        ),
        xaxis=dict(
            title="Total Points",
            tickformat=",",  # Add commas for better readability of numbers
            showgrid=False,  # Remove gridlines for a cleaner look
        ),
        yaxis=dict(
            title="Number of Players",
            showgrid=True,  # Keep gridlines for Y-axis
            zeroline=False,  # Remove the line at y=0
        ),
        margin=dict(l=50, r=50, t=80, b=50),  # Adjust margins for balance
        height=600,  # Set a comfortable height for the plot
    )

    # Add interactive hover template
    fig.update_traces(
        hovertemplate="<b>Total Points</b>: %{x}<br><b>Number of Players</b>: %{y}<extra></extra>"
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    #Player Sign Up Trend
        # Prepare data
    df["joined_time"] = pd.to_datetime(df["joined_time"])  # Ensure joined_time is datetime
    df["joined_date"] = df["joined_time"].dt.date  # Extract date
    signups = df.groupby("joined_date").size().reset_index(name="Number of Players")  # Group by date

    # Create the line chart
    fig = px.line(
        signups,
        x="joined_date",
        y="Number of Players",
        title="Player Sign-Up Trends Over Time",
        labels={"joined_date": "Date", "Number of Players": "Number of Players"},
        template="plotly_dark",
    )

    # Customize the layout
    fig.update_layout(
        title=dict(
            text="Player Sign-Up Trends Over Time",
            # x=0.5,  # Center the title
            font=dict(size=20)
        ),
        xaxis=dict(
            title="Date",
            showgrid=False,  # Remove gridlines for a cleaner look
            tickangle=-45,  # Tilt date labels for better readability
        ),
        yaxis=dict(
            title="Number of Players",
            showgrid=True,  # Keep gridlines for Y-axis
            zeroline=False,  # Remove the line at y=0
        ),
        margin=dict(l=50, r=50, t=80, b=50),  # Adjust margins for balance
        height=600,  # Set a comfortable height for the plot
    )

    # Add a smoother line
    fig.update_traces(
        line=dict(color="royalblue", width=1.5),  # Smoother and thicker line
        hovertemplate="<b>Date</b>: %{x}<br><b>Number of Players</b>: %{y}<extra></extra>"
    )

    # Add annotations for key points (e.g., highest sign-ups)
    max_signups = signups.loc[signups["Number of Players"].idxmax()]
    fig.add_annotation(
        x=max_signups["joined_date"],
        y=max_signups["Number of Players"],
        text=f"Peak: {max_signups['Number of Players']} players",
        showarrow=True,
        arrowhead=2,
        ax=-50,
        ay=-50,
        font=dict(color="white", size=12),
        arrowcolor="white",
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

    #  Favorite Teams of Players
    # Ensure the 'favourite_team' column is numeric (convert strings to NaN where invalid)
    df["favourite_team"] = pd.to_numeric(df["favourite_team"], errors="coerce")

    # Map favorite team indices to EPL team names
    epl_teams = [
       "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton & Hove Albion", "Chelsea", "Crystal Palace", "Everton", "Fulham", "Ipswich Town", "Leicester City", "Liverpool", "Manchester City", "Manchester United", "Newcastle United", "Nottingham Forest", "Southampton", "Tottenham Hotspur", "West Ham United", "Wolverhampton Wanderers"
    ]

    df["favourite_team_name"] = df["favourite_team"].apply(
        lambda x: epl_teams[int(x) - 1] if pd.notnull(x) and 0 < int(x) <= len(epl_teams) else "Unknown"
    )

    # Count favorite teams
    favorite_team_counts = df["favourite_team_name"].value_counts().reset_index()
    favorite_team_counts.columns = ["Team", "Number of Players"]
    # Create a Plotly bar chart with a gradient color scheme
    fig = px.bar(
        favorite_team_counts,
        x="Number of Players",
        y="Team",
        orientation="h",
        title="Favorite Teams of Players",
        color="Number of Players",  # Use player count for a gradient color
        color_continuous_scale="Blues",  # Use a visually appealing gradient
        template="plotly_dark",
        labels={"Number of Players": "Number of Players", "Team": "Team"}
    )
    

    # Customize layout
    fig.update_layout(
        title=dict(
            text="Favorite Teams of Players",
            # x=0.5,  # Center align the title
            font=dict(size=20)
        ),
        xaxis=dict(
            title="Number of Players",
            tickformat=",.0f",  # Add comma formatting for large numbers
            showgrid=False  # Remove grid lines for a cleaner look
        ),
        yaxis=dict(
            title="",
            showgrid=False,
            categoryorder="total ascending"  # Sort teams by total players
        ),
        height=800,  # Adjust height for better spacing
        margin=dict(l=100, r=50, t=80, b=50),  # Adjust margins for cleaner spacing
        coloraxis_colorbar=dict(
            title="Player Count",
            ticks="inside",  # Show ticks inside the color bar
        len=0.5  # Adjust the size of the color bar
    )
)

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    #Total Points Distribution by Favorite Team
    fig = px.box(
    df,
    x="favourite_team_name",
    y="total",
    title="Total Points Distribution by Favorite Team",
    labels={"favourite_team_name": "Favorite Team", "total": "Total Points"},
    template="plotly_dark",
    color="favourite_team_name",
    color_discrete_sequence=px.colors.qualitative.Set3,
)

    fig.update_layout(
        # title_x=0.5,
        font=dict(size=20),
        xaxis=dict(title="Favorite Team", tickangle=-45),  # Tilt team names for readability
        yaxis=dict(title="Total Points"),
        height=600,
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

    #Years active vs total points
    fig = px.box(
    df,
    x="years_active",
    y="total",
    title="Distribution of Total Points by Years Active",
    labels={"years_active": "Years Active", "total": "Total Points"},
    template="plotly_dark",
    color="years_active",
    # color_continuous_scale="Viridis",
    )

    fig.update_layout(
        # title_x=0.5,
        font=dict(size=20),
        xaxis=dict(title="Years Active"),
        yaxis=dict(title="Total Points"),
        height=600,
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
    #Global Rank Distribution
    # Remove invalid ranks (e.g., missing or zero values)
    valid_ranks = df[df["summary_overall_rank"] > 0]  # Filter valid ranks

    # Create a histogram
    fig = px.histogram(
        valid_ranks,
        x="summary_overall_rank",
        nbins=50,  # Adjust the number of bins for granularity
        title="Global Rank Distribution",
        labels={"summary_overall_rank": "Global Rank", "count": "Number of Players"},
        template="plotly_dark",
        color_discrete_sequence=["royalblue"],  # Aesthetic bar color
    )

    
    # Customize the layout
    fig.update_layout(
        title=dict(
            text="Global Rank Distribution",
            # x=0.5,  # Center the title
            font=dict(size=20)
        ),
        xaxis=dict(
            title="Global Rank",
            # type="log",
            showgrid=False,  # Remove gridlines for a cleaner look
            tickformat=",",  # Format numbers with commas
        ),
        yaxis=dict(
            title="Number of Players",
            showgrid=True,  # Keep gridlines for Y-axis
            zeroline=False,  # Remove the line at y=0
        ),
        margin=dict(l=50, r=50, t=80, b=50),  # Adjust margins for balance
        height=600,  # Set a comfortable height for the plot
    )

    # Add interactive hover template
    fig.update_traces(
        hovertemplate="<b>Global Rank</b>: %{x}<br><b>Number of Players</b>: %{y}<extra></extra>"
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")
   
    #Global Distribution of FPL Players
        # Load the data
    # Load the data from the provided CSV file
    file_path = "fpl_country_data_with_country_codes.csv"  # Update with your correct file path
    country_data = pd.read_csv(file_path)
    top_10_countries = country_data.nlargest(10, "National League Player Count")
   # Create a horizontal bar chart to show the number of players in each country
    fig = px.bar(
        top_10_countries,
        x="National League Player Count",  # Number of players
        y="Country",  # Country names
        title="Top 10 Countries by Number of FPL Players",
        labels={"National League Player Count": "Number of Players", "Country": "Country"},
        template="plotly_dark",  # Dark theme for aesthetics
        color="National League Player Count",  # Color bars based on player count
        color_continuous_scale="Viridis",  # Color scale from yellow to red
    )

    # Customize the layout
    fig.update_layout(
        title=dict(
            text="Top 10 Countries by Number of FPL Players",
            # x=0.5,  # Center the title
            font=dict(size=20)
        ),
        xaxis=dict(
            title="Number of Players",
            tickformat=",",  # Format numbers with commas for readability
        ),
        yaxis=dict(
            title="",
            categoryorder="total ascending",  # Sort by the number of players in ascending order
        ),
        height=800,  # Adjust the height for a better view
        margin=dict(l=150, r=50, t=50, b=50),  # Adjust margins for proper spacing
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    # Correct mapping for favorite teams
    team_names = {
        "Arsenal": "Arsenal",
        "Aston Villa": "Aston Villa",
        "Bournemouth": "Bournemouth",
        "Brentford": "Brentford",
        "Brighton & Hove Albion": "Brighton & Hove Albion",
        "Chelsea": "Chelsea",
        "Crystal Palace": "Crystal Palace",
        "Everton": "Everton",
        "Fulham": "Fulham",
        "Ipswich Town": "Ipswich Town",
        "Leicester City": "Leicester City",
        "Liverpool": "Liverpool",
        "Manchester City": "Manchester City",
        "Manchester United": "Manchester United",
        "Newcastle United": "Newcastle United",
        "Nottingham Forest": "Nottingham Forest",
        "Southampton": "Southampton",
        "Tottenham Hotspur": "Tottenham Hotspur",
        "West Ham United": "West Ham United",
        "Wolverhampton Wanderers": "Wolverhampton Wanderers",
    }

    # Sort the data by total points to show the leaderboard
    leaderboard_data = df.sort_values(by="total", ascending=False)
    st.subheader("Leaderboard by Total Points")
    # Add a slider for the number of players to display
    num_players = st.slider("Select number of players to display", min_value=10, max_value=100, value=20)

    # Select the top N players based on the slider value
    leaderboard_display = leaderboard_data.head(num_players)

    # Map the favorite team codes to team names using the dictionary
    leaderboard_display["Favorite Team"] = leaderboard_display["favourite_team_name"].map(team_names)

    # Remove the index column from the table
    leaderboard_display.reset_index(drop=True, inplace=True)

    # Rename the columns for better readability
    leaderboard_display.rename(columns={
        "rank": "Position",
        "entry_name": "Team Name",
        "event_total": "GW 20 Points",
        "total": "Total Points",
        "last_rank": "Last Rank",
        "summary_overall_rank": "Global Rank"
    }, inplace=True)

    # Show the leaderboard table with selected columns (including the favorite team names)
    
    st.dataframe(
        leaderboard_display[["Position", "Team Name", "GW 20 Points", "Total Points", "Last Rank", "Global Rank", "Favorite Team"]],
        width=1000,  # Adjust width for better table readability
    )

    st.markdown("---")

    #GW 20 Leaderboard

    # Sort the data by GW 20 points (event_total)
    leaderboard_data_gw20 = df.sort_values(by="event_total", ascending=False)
    st.subheader("Leaderboard by GW 20 Points")
    # Add a slider for the number of players to display
    num_players_gw20 = st.slider("Select number of players to display for GW 20", min_value=10, max_value=100, value=20)

    # Select the top N players based on the slider value
    leaderboard_display_gw20 = leaderboard_data_gw20.head(num_players_gw20)

    # Map the favorite team codes to team names using the dictionary
    leaderboard_display_gw20["Favorite Team"] = leaderboard_display_gw20["favourite_team_name"].map(team_names)

    # Remove the index column from the table
    leaderboard_display_gw20.reset_index(drop=True, inplace=True)

    # Rename the columns for better readability
    leaderboard_display_gw20.rename(columns={
        "rank": "Position",
        "entry_name": "Team Name",
        "event_total": "GW 20 Points",
        "total": "Total Points",
        "last_rank": "Last Rank"
    }, inplace=True)

    # Show the leaderboard table with selected columns (including the favorite team names)
    
    st.dataframe(
        leaderboard_display_gw20[["Position", "Team Name", "GW 20 Points", "Total Points", "Last Rank", "Favorite Team"]],
        width=1000,  # Adjust width for better table readability
    )
    st.markdown("---")
   
    #Leaderboards by Favourite Teams
    # Sort the data by total points to show the leaderboard
    leaderboard_data = df.sort_values(by="total", ascending=False)
    st.subheader("Leaderboard by Favourite Teams")

    # Add a dropdown to select a team
    team_selection = st.selectbox("Select a Team", list(team_names.values()))

    # Filter the leaderboard data by the selected team
    filtered_data = leaderboard_data[leaderboard_data["favourite_team_name"] == team_selection]

    # Add a slider for the number of players to display
    num_players = st.slider(f"Select number of top players for {team_selection}", min_value=10, max_value=100, value=20)

    # Select the top N players based on the slider value
    leaderboard_display = filtered_data.head(num_players)

    # Map the favorite team codes to team names using the dictionary
    leaderboard_display["Favorite Team"] = leaderboard_display["favourite_team_name"].map(team_names)

    # Remove the original 'favourite_team_name' column to avoid duplication
    leaderboard_display.drop(columns=["favourite_team_name"], inplace=True)

    # Remove the index column from the table
    leaderboard_display.reset_index(drop=True, inplace=True)

    # Rename the columns for better readability
    leaderboard_display.rename(columns={
        "rank": "Position",
        "entry_name": "Team Name",
        "event_total": "GW 20 Points",
        "total": "Total Points",
        "last_rank": "Last Rank",
    }, inplace=True)

    # Show the leaderboard table with selected columns (including the favorite team names)
    st.subheader(f"Top Players for {team_selection}")
    st.dataframe(
        leaderboard_display[["Position", "Team Name", "GW 20 Points", "Total Points", "Last Rank", "Favorite Team"]],
        width=1000,  # Adjust width for better table readability
    )


with tab3:

   # Add a title for the search tab
    st.subheader("Search for Player by FPL ID")

    # Create an input box for FPL ID (entry)
    fpl_id = st.text_input("Enter the FPL ID:").strip()

    # Search the dataframe when the FPL ID is entered
    if fpl_id:
        # Ensure the entered value is an integer, as FPL ID (entry) should be numeric
        try:
            fpl_id = int(fpl_id)  # Convert to integer
            
            # Filter the dataframe based on the FPL ID
            result = df[df["entry"] == fpl_id]
            
            if result.empty:
                st.warning(f"No player found with FPL ID {fpl_id}.")
            else:
                # Extract the team name from the result
                team_name = result["entry_name"].values[0]
                
                # Clean the DataFrame to show necessary details
                player_data = result[['entry_name', 'rank', 'total', 'event_total', 'years_active', 'favourite_team_name', 'last_rank', 'summary_overall_rank']]
                
                # Map favourite team codes to team names
                team_names = {
                    "Arsenal": "Arsenal", "Aston Villa": "Aston Villa", "Bournemouth": "Bournemouth",
                    "Brentford": "Brentford", "Brighton & Hove Albion": "Brighton & Hove Albion", "Chelsea": "Chelsea",
                    "Crystal Palace": "Crystal Palace", "Everton": "Everton", "Fulham": "Fulham", "Ipswich Town": "Ipswich Town",
                    "Leicester City": "Leicester City", "Liverpool": "Liverpool", "Manchester City": "Manchester City",
                    "Manchester United": "Manchester United", "Newcastle United": "Newcastle United", "Nottingham Forest": "Nottingham Forest",
                    "Southampton": "Southampton", "Tottenham Hotspur": "Tottenham Hotspur", "West Ham United": "West Ham United",
                    "Wolverhampton Wanderers": "Wolverhampton Wanderers"
                }

                # Map favourite team codes to team names
                player_data["Favorite Team"] = player_data["favourite_team_name"].map(team_names)
                
                # Remove the duplicate 'favourite_team_name' column
                player_data.drop(columns=["favourite_team_name"], inplace=True)

                # Rename columns for readability
                player_data.rename(columns={
                    'entry_name': 'Team Name', 'rank': 'Position', 'total': 'Total Points', 
                    'event_total': 'GW 20 Points', 'years_active': 'Years Active', 'last_rank': 'Last Rank', 'summary_overall_rank': 'Overall Rank'
                }, inplace=True)

                # Show the player information with a more aesthetic and clean layout
                st.write(f"Player Information for {team_name}")

                # Display the data in a table format with improved styling
                st.markdown("""
                    <style>
                        .stDataFrame > div {
                            margin-top: 0;
                        }
                        .stDataFrame table {
                            width: 100%;
                            border-collapse: collapse;
                        }
                        .stDataFrame th, .stDataFrame td {
                            padding: 10px;
                            text-align: left;
                            border-bottom: 1px solid #ddd;
                        }
                        .stDataFrame th {
                            background-color: #222222;
                            color: white;
                        }
                        .stDataFrame td {
                            color: white;
                        }
                        .stDataFrame tr:hover {
                            background-color: #444444;
                        }
                    </style>
                """, unsafe_allow_html=True)

                st.dataframe(
                    player_data[["Position", "Overall Rank", "Team Name", "GW 20 Points", "Total Points", "Last Rank", "Years Active", "Favorite Team"]],
                    width=1000,  # Adjust width for better table readability
                )
                
        except ValueError:
            st.error("Please enter a valid FPL ID (numeric only).")