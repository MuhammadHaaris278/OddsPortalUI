import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import zipfile
import io
import platform
import sys
import traceback
import os

# Add the current directory to path to import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.user_agent_pool import get_random_user_agent
    from core.utils import get_logger
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# API configuration
API_URL = "https://oddsportalui.onrender.com/"  # Update this if the API runs elsewhere
logger = get_logger()


def map_url_to_league(match):
    """Map match_url to the correct league name if league is 'Unknown'."""
    url = match.get('match_url', '').lower()
    league = match.get('league', 'Unknown')

    # If league is already set correctly (e.g., NFL, NCAA, WNBA), keep it
    if league in ["NFL", "NCAA", "WNBA"]:
        return league

    # Map based on URL patterns
    if 'football' in url:
        return "Football"
    elif 'basketball' in url:
        return "Basketball"
    elif 'tennis' in url:
        return "Tennis"
    elif 'futsal' in url:
        return "Futsal"
    elif 'baseball' in url:
        return "Baseball"
    else:
        return league  # Fallback to original league if no match


def fetch_matches_from_api():
    """Fetch matches from the API and correct league names."""
    try:
        response = requests.get(f"{API_URL}/matches")
        response.raise_for_status()
        data = response.json()
        if data["status"] == "success":
            # Correct league names for matches
            corrected_matches = []
            for match in data["matches"]:
                corrected_match = match.copy()  # Create a copy to avoid modifying original
                if corrected_match.get('league') == "Unknown":
                    corrected_match['league'] = map_url_to_league(
                        corrected_match)
                corrected_matches.append(corrected_match)
            return corrected_matches
        else:
            raise Exception(data.get("detail", "Unknown error from API"))
    except Exception as e:
        raise Exception(f"Failed to fetch matches from API: {str(e)}")


def trigger_scrape():
    """Trigger a new scrape via the API and correct league names."""
    try:
        response = requests.post(f"{API_URL}/scrape")
        response.raise_for_status()
        data = response.json()
        if data["status"] == "success":
            # Correct league names for matches
            corrected_matches = []
            for match in data["matches"]:
                corrected_match = match.copy()
                if corrected_match.get('league') == "Unknown":
                    corrected_match['league'] = map_url_to_league(
                        corrected_match)
                corrected_matches.append(corrected_match)
            return corrected_matches
        else:
            raise Exception(data.get("detail", "Unknown error from API"))
    except Exception as e:
        raise Exception(f"Failed to trigger scrape: {str(e)}")


def generate_sample_data():
    """Generate sample data when scraping fails or in test mode."""
    sample_matches = []
    sports = ["NFL", "NBA", "WNBA", "NCAA", "Tennis",
              "Football", "Basketball", "Baseball", "Futsal"]
    teams = {
        "NFL": [("Kansas City Chiefs", "Buffalo Bills"), ("Green Bay Packers", "Dallas Cowboys")],
        "NBA": [("Los Angeles Lakers", "Boston Celtics"), ("Golden State Warriors", "Miami Heat")],
        "WNBA": [("Las Vegas Aces", "New York Liberty"), ("Seattle Storm", "Phoenix Mercury")],
        "NCAA": [("Duke Blue Devils", "North Carolina Tar Heels"), ("UCLA Bruins", "USC Trojans")],
        "Tennis": [("Novak Djokovic", "Rafael Nadal"), ("Serena Williams", "Venus Williams")],
        "Football": [("Manchester United", "Liverpool"), ("Barcelona", "Real Madrid")],
        "Basketball": [("Team Phoenix", "Team Thunder"), ("Team Lightning", "Team Storm")],
        "Baseball": [("New York Yankees", "Boston Red Sox"), ("Los Angeles Dodgers", "San Francisco Giants")],
        "Futsal": [("Team Alpha", "Team Beta"), ("Team Gamma", "Team Delta")]
    }

    for sport in sports:
        for i, (team1, team2) in enumerate(teams[sport]):
            sample_matches.append({
                "datetime": (datetime.now() + timedelta(hours=i+1)).isoformat(),
                "league": sport,
                "team1": team1,
                "team2": team2,
                "odds": ["+150", "-110", "+200"],
                "match_url": f"https://www.oddsportal.com/sample/{sport.lower()}"
            })

    return sample_matches


# Page configuration
st.set_page_config(
    page_title="OddsPortal Scraper",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    .navbar {
        background-color: #1e3d59;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    .navbar h3 {
        color: white;
        margin: 0;
        text-align: center;
    }
    
    .sport-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        min-width: 150px;
    }
    
    .footer {
        background-color: #1e3d59;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-top: 3rem;
    }
    
    .download-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-top: 2rem;
    }
    
    .stButton > button {
        background-color: #667eea;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #5a6fd8;
        transform: translateY(-2px);
    }
    
    .error-section {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    
    .success-section {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    
    .terminal-container {
        background-color: #1e1e1e;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #333;
    }
    
    .terminal-header {
        background-color: #2d2d2d;
        padding: 0.5rem;
        border-radius: 5px 5px 0 0;
        color: #fff;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .terminal-content {
        background-color: #000;
        color: #00ff00;
        padding: 1rem;
        border-radius: 0 0 5px 5px;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        max-height: 300px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = None
if 'scraping_in_progress' not in st.session_state:
    st.session_state.scraping_in_progress = False
if 'last_scrape_time' not in st.session_state:
    st.session_state.last_scrape_time = None
if 'last_error' not in st.session_state:
    st.session_state.last_error = None
if 'terminal_logs' not in st.session_state:
    st.session_state.terminal_logs = []

# Navbar
st.markdown("""
<div class="navbar">
    <h3>🏆 OddsPortal Scraper Dashboard</h3>
</div>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="main-header">
    <h1>🎯 OddsPortal Data Scraper</h1>
    <p>Automated sports betting odds scraper with stealth capabilities</p>
    <p>Scrapes matches from multiple sports leagues for the next 24 hours</p>
</div>
""", unsafe_allow_html=True)

# Show system information
st.markdown("## 🖥️ System Information")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Operating System", platform.system())
with col2:
    st.metric("Python Version",
              f"{sys.version_info.major}.{sys.version_info.minor}")
with col3:
    st.metric("Streamlit Version", st.__version__)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("## 📊 Scraping Control Panel")

    # Test mode toggle
    test_mode = st.checkbox("🧪 Test Mode (Generate Sample Data)",
                            value=True,  # Default to True for simplicity
                            help="Use this to test the UI with sample data instead of calling the API.")

    # Scraping controls
    button_text = "🧪 Generate Sample Data" if test_mode else "🚀 Start Scraping"
    button_help = "Generate sample data for testing" if test_mode else "Start scraping via API"

    if st.button(button_text, disabled=st.session_state.scraping_in_progress, help=button_help):
        st.session_state.scraping_in_progress = True
        st.session_state.last_error = None
        st.session_state.terminal_logs = []

        spinner_text = "🔄 Generating sample data..." if test_mode else "🔄 Fetching odds data from API..."

        with st.spinner(spinner_text):
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Create terminal log container
            terminal_container = st.container()
            with terminal_container:
                st.markdown("### 🖥️ Terminal Logs")
                log_display = st.empty()

            try:
                if test_mode:
                    # Generate sample data
                    status_text.text("Generating sample sports data...")
                    st.session_state.terminal_logs.append(
                        f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Starting sample data generation...")
                    log_display.code(
                        '\n'.join(st.session_state.terminal_logs[-10:]))
                    progress_bar.progress(30)

                    status_text.text("Creating mock matches...")
                    st.session_state.terminal_logs.append(
                        f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Creating mock matches for all sports...")
                    log_display.code(
                        '\n'.join(st.session_state.terminal_logs[-10:]))
                    progress_bar.progress(60)

                    matches = generate_sample_data()
                    progress_bar.progress(100)
                    status_text.text("✅ Sample data generated successfully!")
                    st.session_state.terminal_logs.append(
                        f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Sample data generation completed! Generated {len(matches)} matches")
                    log_display.code(
                        '\n'.join(st.session_state.terminal_logs[-10:]))

                else:
                    # Check API health
                    status_text.text("Checking API availability...")
                    st.session_state.terminal_logs.append(
                        f"[{datetime.now().strftime('%H:%M:%S')}] 🔌 Checking API availability...")
                    log_display.code(
                        '\n'.join(st.session_state.terminal_logs[-10:]))
                    try:
                        response = requests.get(f"{API_URL}/health")
                        response.raise_for_status()
                        progress_bar.progress(20)
                    except Exception as e:
                        raise Exception(f"API is not available: {str(e)}")

                    # Trigger scrape via API
                    status_text.text("Triggering scrape via API...")
                    st.session_state.terminal_logs.append(
                        f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Triggering scrape via API...")
                    log_display.code(
                        '\n'.join(st.session_state.terminal_logs[-10:]))
                    progress_bar.progress(40)

                    matches = trigger_scrape()
                    progress_bar.progress(80)

                    status_text.text("Processing API response...")
                    st.session_state.terminal_logs.append(
                        f"[{datetime.now().strftime('%H:%M:%S')}] 📋 Processing API response...")
                    log_display.code(
                        '\n'.join(st.session_state.terminal_logs[-10:]))

                # Store results
                st.session_state.scraped_data = matches
                st.session_state.last_scrape_time = datetime.now()

                progress_bar.progress(100)
                completion_text = "✅ Sample data ready!" if test_mode else "✅ Scraping completed successfully!"
                status_text.text(completion_text)

                success_text = f"🎉 Successfully generated {len(matches)} sample matches!" if test_mode else f"🎉 Successfully fetched {len(matches)} matches from API!"
                st.success(success_text)

            except Exception as e:
                st.session_state.last_error = f"{str(e)}\n\nFull traceback:\n{traceback.format_exc()}"
                error_msg = f"❌ Error during {'sample data generation' if test_mode else 'API scraping'}: {str(e)}"
                st.error(error_msg)
                st.session_state.terminal_logs.append(
                    f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {str(e)}\n{traceback.format_exc()}")
                log_display.code(
                    '\n'.join(st.session_state.terminal_logs[-10:]))

                # Show detailed error for debugging
                with st.expander("🔍 Error Details"):
                    st.code(f"{str(e)}\n\n{traceback.format_exc()}")

                # Offer fallback option
                if not test_mode:
                    st.info(
                        "💡 You can enable 'Test Mode' to generate sample data and test the UI functionality.")

            finally:
                st.session_state.scraping_in_progress = False
                progress_bar.empty()
                status_text.empty()

with col2:
    st.markdown("## 📈 Stats")

    if st.session_state.scraped_data:
        total_matches = len(st.session_state.scraped_data)

        # Group by league
        leagues = {}
        for match in st.session_state.scraped_data:
            league = match.get('league', 'Unknown')
            leagues[league] = leagues.get(league, 0) + 1

        # Display stats
        st.metric("Total Matches", total_matches)
        st.metric("Sports Covered", len(leagues))

        if st.session_state.last_scrape_time:
            st.metric("Last Scrape",
                      st.session_state.last_scrape_time.strftime("%H:%M:%S"))

        # League breakdown
        st.markdown("### League Breakdown")
        for league, count in leagues.items():
            st.write(f"**{league}**: {count} matches")
    else:
        st.info("No data available. Run scraping or generate sample data first.")

    # Show last error if any
    if st.session_state.last_error:
        st.markdown("### ⚠️ Last Error")
        st.error(st.session_state.last_error[:100] + "..." if len(
            st.session_state.last_error) > 100 else st.session_state.last_error)

# Data Display and Download Section
if st.session_state.scraped_data:
    st.markdown("---")
    st.markdown("## 📁 Scraped Data & Downloads")

    # Group matches by sport/league
    sports_data = {}
    for match in st.session_state.scraped_data:
        sport = match.get('league', 'Unknown').lower()
        if sport not in sports_data:
            sports_data[sport] = []
        sports_data[sport].append(match)

    # Create tabs for different sports
    if sports_data:
        tabs = st.tabs(list(sports_data.keys()))

        for i, (sport, matches) in enumerate(sports_data.items()):
            with tabs[i]:
                st.markdown(
                    f"### {sport.upper()} Matches ({len(matches)} total)")

                # Convert to DataFrame for display
                df_data = []
                for match in matches:
                    df_data.append({
                        'DateTime': match.get('datetime', ''),
                        'Team 1': match.get('team1', ''),
                        'Team 2': match.get('team2', ''),
                        'Odds': ', '.join(match.get('odds', [])),
                        'URL': match.get('match_url', '')
                    })

                df = pd.DataFrame(df_data)
                st.dataframe(df, use_container_width=True)

                # Download buttons for individual sports
                col1, col2 = st.columns(2)

                with col1:
                    # CSV download
                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)
                    st.download_button(
                        label=f"📊 Download {sport.upper()} CSV",
                        data=csv_buffer.getvalue(),
                        file_name=f"{sport}_matches_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )

                with col2:
                    # JSON download
                    json_data = json.dumps(
                        matches, indent=2, ensure_ascii=False)
                    st.download_button(
                        label=f"📋 Download {sport.upper()} JSON",
                        data=json_data,
                        file_name=f"{sport}_matches_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                        mime="application/json"
                    )

    # Download All Files Section
    st.markdown("---")
    st.markdown("## 📦 Download All Files")

    def create_zip_file():
        """Create a zip file containing all CSV and JSON files."""
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')

            for sport, matches in sports_data.items():
                # Create CSV
                df_data = []
                for match in matches:
                    df_data.append({
                        'DateTime': match.get('datetime', ''),
                        'Team 1': match.get('team1', ''),
                        'Team 2': match.get('team2', ''),
                        'Odds': ', '.join(match.get('odds', [])),
                        'URL': match.get('match_url', '')
                    })

                df = pd.DataFrame(df_data)

                # Add CSV to zip
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                zip_file.writestr(
                    f"{sport}_matches_{timestamp}.csv", csv_buffer.getvalue())

                # Add JSON to zip
                json_data = json.dumps(matches, indent=2, ensure_ascii=False)
                zip_file.writestr(
                    f"{sport}_matches_{timestamp}.json", json_data)

            # Add consolidated file
            all_matches_df = pd.DataFrame([
                {
                    'DateTime': match.get('datetime', ''),
                    'League': match.get('league', ''),
                    'Team 1': match.get('team1', ''),
                    'Team 2': match.get('team2', ''),
                    'Odds': ', '.join(match.get('odds', [])),
                    'URL': match.get('match_url', '')
                }
                for match in st.session_state.scraped_data
            ])

            consolidated_csv = io.StringIO()
            all_matches_df.to_csv(consolidated_csv, index=False)
            zip_file.writestr(
                f"consolidated_matches_{timestamp}.csv", consolidated_csv.getvalue())

            consolidated_json = json.dumps(
                st.session_state.scraped_data, indent=2, ensure_ascii=False)
            zip_file.writestr(
                f"consolidated_matches_{timestamp}.json", consolidated_json)

        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    if st.button("📥 Prepare Download Package"):
        with st.spinner("Creating download package..."):
            zip_data = create_zip_file()

            st.download_button(
                label="⬇️ Download All Files (ZIP)",
                data=zip_data,
                file_name=f"oddsportal_scraper_data_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
                mime="application/zip"
            )

            st.success("📦 Download package ready!")

# Information Section
st.markdown("---")
st.markdown("## ℹ️ About This Scraper")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **🛡️ Stealth Features:**
    - Randomized user agents
    - Request delays and timing
    - Headless browser automation
    - Anti-detection measures
    """)

with col2:
    st.markdown("""
    **📊 Supported Sports:**
    - Football (Soccer)
    - Basketball (NBA, WNBA, NCAA)
    - American Football (NFL, NCAA)
    - Tennis
    - Baseball
    - Futsal
    """)

st.markdown("""
**⏰ Data Coverage:**
- Scrapes matches for the next 24 hours
- Updates odds and team information
- Exports in both CSV and JSON formats
- Consolidated and sport-specific files
""")

# Troubleshooting Section
st.markdown("---")
st.markdown("## 🔧 Troubleshooting")

with st.expander("💡 Common Issues & Solutions"):
    st.markdown("""
    **Issue: API Not Responding**
    - **Solution 1**: Ensure the API is running at `https://oddsportalui.onrender.com`
    - **Solution 2**: Check the API logs for errors
    - **Solution 3**: Restart the API server:
      ```bash
      python api.py
      ```
    - **Solution 4**: Verify network connectivity

    **Issue: No Data Returned**
    - Try enabling Test Mode to generate sample data
    - Check if the API has fresh data by triggering a new scrape
    - Verify the API endpoint is accessible

    **Issue: Module Import Errors**
    - Verify all project files are in the correct directories
    - Check that `core/` and `utils/` folders exist
    - Ensure all `__init__.py` files are present

    **Issue: Incorrect League Names**
    - Ensure the API is returning data with URLs that include sport names
    - Verify that test mode is disabled to fetch real data
    - Check the API response for correct `match_url` values
    """)

with st.expander("🐛 Debug Information"):
    st.markdown("**Environment Information:**")
    st.code(f"""
Python Version: {sys.version}
Streamlit Version: {st.__version__}
Platform: {platform.system()} {platform.release()}
Architecture: {platform.machine()}
Current Directory: {os.getcwd()}
API URL: {API_URL}
""")

    if st.button("🔍 Check Dependencies"):
        dependency_checks = []

        # Check requests
        try:
            import requests
            dependency_checks.append(
                ("✅ Requests", f"Version {requests.__version__}"))
        except ImportError as e:
            dependency_checks.append(
                ("❌ Requests", f"Not installed: {str(e)}"))

        # Check pandas
        try:
            import pandas as pd
            dependency_checks.append(("✅ Pandas", f"Version {pd.__version__}"))
        except ImportError as e:
            dependency_checks.append(("❌ Pandas", f"Not installed: {str(e)}"))

        # Check core modules
        try:
            from core.utils import get_logger
            dependency_checks.append(("✅ Core modules", "Accessible"))
        except ImportError as e:
            dependency_checks.append(
                ("❌ Core modules", f"Not accessible: {str(e)}"))

        # Check utils modules
        try:
            from utils.user_agent_pool import get_random_user_agent
            dependency_checks.append(("✅ Utils modules", "Accessible"))
        except ImportError as e:
            dependency_checks.append(
                ("❌ Utils modules", f"Not accessible: {str(e)}"))

        # Check API connectivity
        try:
            response = requests.get(f"{API_URL}/health")
            response.raise_for_status()
            dependency_checks.append(
                ("✅ API Connectivity", "API is reachable"))
        except Exception as e:
            dependency_checks.append(
                ("❌ API Connectivity", f"Failed to reach API: {str(e)}"))

        # Display results
        for status, message in dependency_checks:
            if "✅" in status:
                st.success(f"{status}: {message}")
            else:
                st.error(f"{status}: {message}")

# Footer
st.markdown("""
<div class="footer">
    <h3>🏆 OddsPortal Scraper</h3>
    <p>Dynamic data scraping with stealth capabilities</p>
    <p>Built with ❤️ using Streamlit, FastAPI, and Python</p>
    <p>© 2024 - Automated Sports Data Collection</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with additional info
with st.sidebar:
    st.markdown("## 🔧 Settings")

    # Auto-refresh option
    auto_refresh = st.checkbox("Auto-refresh every 30 minutes")

    if auto_refresh:
        st.info("⏰ Auto-refresh enabled")

    st.markdown("---")
    st.markdown("## 📋 Quick Info")
    st.markdown(f"""
    - **Platform**: {platform.system()}
    - **Next scrape**: Next 24 hours
    - **Stealth mode**: Always active
    - **Output formats**: CSV & JSON
    - **Sports covered**: 6+ leagues
    - **API URL**: {API_URL}
    """)

    if st.session_state.last_scrape_time:
        st.markdown(
            f"**Last run**: {st.session_state.last_scrape_time.strftime('%Y-%m-%d %H:%M:%S')}")

    st.markdown("---")
    st.markdown("## 🚀 Quick Actions")

    if st.button("🔄 Refresh Page"):
        st.rerun()

    if st.button("🗑️ Clear Data"):
        st.session_state.scraped_data = None
        st.session_state.last_scrape_time = None
        st.session_state.last_error = None
        st.success("Data cleared!")
        st.rerun()

    if st.button("🧪 Force Test Mode"):
        st.session_state.scraped_data = generate_sample_data()
        st.session_state.last_scrape_time = datetime.now()
        st.success("Sample data generated!")
        st.rerun()

# Auto-refresh logic
if auto_refresh and st.session_state.last_scrape_time:
    time_diff = datetime.now() - st.session_state.last_scrape_time
    if time_diff.total_seconds() > 1800:  # 30 minutes
        st.rerun()
