#imports
import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor
from streamlit_lottie import st_lottie
import pandas as pd
import hashlib
import gspread
import os
import base64
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import json
import streamlit.components.v1 as components
import re

# --- Streamlit App UI ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = "guest"
if "page" not in st.session_state: st.session_state.page = "home"
if "viewing_profile" not in st.session_state: st.session_state.viewing_profile = None

# Set your admin username here
ADMIN_USERNAME = "admin_aixient" # Replace with your actual admin username

tags = [
    'AI', 'design', 'art', 'vector', 'free-tier', 'educational', 'library', 'history', 'research', 'free',
    'creative', 'film', 'visual-database', 'paid', 'science', 'illustration', 'medical', 'gaming',
    'multiplayer', 'online', 'tools', 'file-conversion', 'utility', 'technology', 'hardware', 'computer',
    'shopping', 'travel', 'exploration', 'inspiration', 'interior-design', 'home', 'food', 'cooking',
    'recipes', 'business', 'video-creation', 'animation', 'entertainment', 'movies', 'television',
    'search-engine', '3d', 'packaging', 'mockup', 'development', 'coding', 'education', 'nostalgia',
    'retro', 'video', 'automotive', 'diy', 'repair', 'planning', 'maps', 'data-science', 'productivity',
    'organization', 'notes', 'mobile', 'logo', 'graphics', 'assets', 'icons', 'kids', 'programming',
    'audio', 'music', 'tabletop', 'rpg', 'storytelling', 'IDE', 'fitness', 'health', 'workout',
    'relaxation', 'simulation', 'color', 'automation', 'web-design', 'UI-UX', 'aviation', 'toys',
    'app', 'geography', 'hobby', 'manual', 'data-visualization', 'personal', 'interactive',
    'free-trial', 'statistics', 'comparison', 'procedural', 'typing', 'file-management', 'fighting-game',
    'photo-editing', 'anatomy', 'drawing', 'printable', 'anime', 'knowledge', 'puzzles', 'pdf',
    'open-source', 'library', 'tutorials', 'community', 'language', 'reference', 'study',
    'transcription', 'portfolio', 'images', 'stock-photos', 'math', 'homework', 'radio', 'modeling',
    'collaboration', 'consumer', 'forms', 'presentation', 'virtual', 'web-dev', 'virtual-reality',
    'resources', 'engineering', 'courses', 'university', 'student', 'mind-mapping', 'browser',
    'marketing', 'SEO'
]

websites = []
website_descriptions = []
website_freeness = []
website_tags = []
# --- Globals and Secrets ---
G_SHEET_NAME = "aixient-users"
# Configure the main page layout
st.set_page_config(
    page_title="Aixient",
    layout="wide",
    page_icon="https://avatars.githubusercontent.com/u/36308163?s=200&v=4",
)
st.markdown("""
<style>
/* Hides Streamlit's default elements like the "Made with Streamlit" footer and main menu */
#MainMenu {visibility: hidden;} !important;
footer {visibility: hidden;} !important;

/* Hides the "portal" element, which can appear as a bar at the bottom */
div[data-testid="portal"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

#tittle
st.markdown("""
<style>
.stApp {
    margin-top: -65px;
}
div.block-container{
    padding-top:2rem;
    padding-bottom:0rem;
}
.title {
    text-align: center;
    font-size: 200px !important;
    font-weight: bold;
    background: linear-gradient(90deg, rgba(5, 120, 156) 0%, rgba(237, 83, 119) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)
#hook
st.markdown("""
<style>
.standard {
    text-align: center;
    font-size: 50px !important;  /* Changed to ensure font size is applied */
    font-weight: bold;
    background: linear-gradient(90deg,rgba(5, 120, 156) 0%, rgba(237, 83, 119) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)
#searchbar type beat :skull:
st.markdown("""
<style>
/* This targets the focused state of the container around the input */
div[data-testid="stTextInput"] > div:focus-within {
    box-shadow: none !important;
}

/* Also ensure the inner input element doesn't have a highlight */
div[data-testid="stTextInput"] > div > input:focus {
    box-shadow: none !important;
    outline: none !important;
}

/* If you want a subtle highlight that matches the background */
div[data-testid="stTextInput"] > div:focus-within {
    border-color: #0E1117 !important;
    box-shadow: 0 0 0 2px #0E1117 !important;
}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
/* This targets the main container of the Streamlit text input.
We'll use a pseudo-element to create the gradient border effect.
*/
div.stTextInput > div > div {
    position: relative; /* Needed for the absolute positioning of the pseudo-element */
    padding: 2px; /* This creates the visible 'border' area */
    border-radius: 23px; /* Matches the inner input's border-radius */
    background: transparent; /* Initially transparent */
    transition: background 0.5s ease-in-out; /* Smooth transition for the gradient change */
}

/* This is the inner input field itself */
div.stTextInput > div > div > input {
    width: 100%;
    background-color: #1a1a1a;  /* Dark background color */
    color: #ffffff;             /* White text color */
    border: none;               /* Remove the default border to let the gradient show */
    border-radius: 23px;        /* Slightly smaller to fit inside the parent's border */
    padding: 10px 20px;         /* Padding inside the search bar */
    font-size: 16px;            /* Larger font size */
    outline: none;              /* Remove browser outline on focus */
}

/* Hover effect on the container to show the gradient border */
div.stTextInput > div > div:hover {
    background: linear-gradient(90deg, rgba(5, 120, 156) 0%, rgba(237, 83, 119) 100%);

}
div.stTextInput > div > div:focus-within {
    background: linear-gradient(90deg, rgba(5, 120, 156) 0%, rgba(237, 83, 119) 100%);

}

/* Focus effect on the input to also show the gradient border on its parent */
div.stTextInput > div > div > input:focus + div.stTextInput > div > div {
    background: linear-gradient(90deg, rgba(5, 120, 156) 0%, rgba(237, 83, 119) 100%);

}
/* Focus effect on the input to also show the gradient border on its parent */
div.stTextInput > div > div > input:focus-within + div.stTextInput > div > div {
    background: linear-gradient(90deg, rgba(5, 120, 156) 0%, rgba(237, 83, 119) 100%);

}
</style>
""", unsafe_allow_html=True)
#segmented control
st.markdown("""
<style>
/* This targets the currently active segmented button */
[data-testid="stBaseButton-segmented_controlActive"] {
    /* Sets a semi-transparent background. Adjust the last number (0.2) for more or less transparency */
    background-color: #0E1117 !important;
    
    /* Adds a solid border with the specified color */
    border: 3px solid rgba(5, 120, 156) !important;
}

/* This targets the text within the active button */
[data-testid="stBaseButton-segmented_controlActive"] p {
    color: #FFFFFF !important; /* Sets the font color to the solid blue */

}
</style>
""", unsafe_allow_html=True)
#toast warnings
st.markdown("""
<style>
/* This targets the specific toast container */
div[data-testid="stToast"] {
    background-color: rgba(62, 59, 22, 1) !important;
    color: rgba(225, 224, 116, 1) !important;
    font-weight: bold !important;
}
</style>
""", unsafe_allow_html=True)

# --- Authentication and Database Functions ---
@st.cache_resource
def get_db():
    """Connects to the Google Sheet and returns the worksheet."""
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
        client = gspread.authorize(credentials)
        sheet = client.open(G_SHEET_NAME).get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

@st.cache_data(ttl=600)
def get_dataframe(_sheet):
    """Fetches all records from the Google Sheet and returns a DataFrame."""
    try:
        data = _sheet.get_all_records()
        df = pd.DataFrame(data)
        
        required_columns = ['username', 'views', 'viewed_profiles']
        if not all(col in df.columns for col in required_columns) and not df.empty:
            st.error("Error: Required columns not found in Google Sheet. Please ensure the column headers are set up correctly.")
            return pd.DataFrame()
        
        return df
    except Exception as e:
        st.error(f"Error reading from Google Sheets: {e}")
        return pd.DataFrame()

def update_sheet_and_clear_cache(df, sheet):
    """
    Updates the entire Google Sheet with the new DataFrame,
    ensuring all data is treated as strings to prevent formatting issues.
    """
    # Convert all DataFrame values to strings
    df_string = df.astype(str)
    
    # Prepend the column headers and convert the entire thing to a list of lists
    data_to_write = [df_string.columns.values.tolist()] + df_string.values.tolist()
    
    # Update the sheet
    sheet.update(data_to_write)
    
    # Clear the cache
    st.cache_data.clear()
# --- Password Hashing and User Management Functions ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, hashed_password):
    return hash_password(password) == hashed_password

def add_user(username, password):
    sheet = get_db()
    if sheet is None: return False, "Database connection failed."
    df = get_dataframe(sheet)
    if username in df["username"].values:
        return False, "Username already exists."
    
    new_user = pd.DataFrame([{
        "username": username,
        "hashed_password": hash_password(password),
        "profile_pic_path": "",
        "views": "",
        "viewed_profiles": "",
        "uploaded_websites": "",
        "description": "",
        "freeness": "",
        "tags": "",
        "uploaded_datetime": "",
        "status": "approved", # New user is automatically approved
    }])
    df = pd.concat([df, new_user], ignore_index=True)
    update_sheet_and_clear_cache(df, sheet)
    return True, "Account created successfully!"

def verify_user(username, password):
    sheet = get_db()
    if sheet is None: return False
    df = get_dataframe(sheet)
    user_data = df[df["username"] == username]
    if not user_data.empty:
        hashed_password = user_data["hashed_password"].values[0]
        return check_password(password, hashed_password)
    return False

# NEW FUNCTION FOR UPDATING STATUS
def update_website_status(username, link_to_update, new_status):
    sheet = get_db()
    if sheet is None: return False, "Database connection failed."
    df = get_dataframe(sheet)

    user_index = df[df["username"] == username].index[0]
    uploaded_websites_list = [w.strip() for w in str(df.loc[user_index, 'uploaded_websites']).split(',') if w.strip()]
    
    if link_to_update in uploaded_websites_list:
        link_index = uploaded_websites_list.index(link_to_update)
        
        # Safely split the status column
        status_list = [s.strip() for s in str(df.loc[user_index, 'status']).split(',') if s.strip()]
        
        # Ensure the status list is long enough for the new website
        if len(status_list) <= link_index:
            status_list.extend(['pending'] * (link_index - len(status_list) + 1))
        
        # Update the status
        status_list[link_index] = new_status
        df.loc[user_index, 'status'] = ','.join(status_list)

        update_sheet_and_clear_cache(df, sheet)
        return True, f"Website status updated to '{new_status}'."
    return False, "Website not found for this user."

# --- Website Management Functions ---
def add_website(current_user, new_link, description, freeness, tags):
    """
    Adds a new website with its details to the user's row in the Google Sheet.
    This function correctly formats tags and views to avoid data corruption.
    """
    sheet = get_db()
    if sheet is None:
        return False, "Database connection failed."
    
    df = get_dataframe(sheet)
    
    if current_user not in df["username"].values:
        return False, "User not found."
    
    user_index = df[df["username"] == current_user].index[0]

    # Helper function to safely split comma-separated strings
    def safe_split(column_value):
        value_str = str(column_value)
        if not value_str or pd.isna(column_value) or value_str.lower() == 'nan':
            return []
        return [item.strip() for item in value_str.split(',') if item.strip()]

    # Helper function to parse JSON-formatted tags
    def safe_parse_json_list(column_value, delimiter='~'):
        value_str = str(column_value)
        if not value_str or pd.isna(column_value) or value_str.lower() == 'nan':
            return []
            
        parsed_lists = []
        for json_str in value_str.split(delimiter):
            try:
                parsed_lists.append(json.loads(json_str))
            except (json.JSONDecodeError, TypeError):
                st.warning(f"Error parsing JSON for tags: {json_str}. Skipping.")
                continue
        return parsed_lists

    # Retrieve existing data from the DataFrame
    uploaded_websites_list = safe_split(df.loc[user_index, 'uploaded_websites'])
    description_list = safe_split(df.loc[user_index, 'description'])
    freeness_list = safe_split(df.loc[user_index, 'freeness'])
    tags_list_of_lists = safe_parse_json_list(df.loc[user_index, 'tags'])
    datetime_list = safe_split(df.loc[user_index, 'uploaded_datetime'])
    status_list = safe_split(df.loc[user_index, 'status'])
    views_list = safe_split(df.loc[user_index, 'views'])

    if new_link in uploaded_websites_list:
        return False, "Website already exists in your list."

    # Append the new data
    uploaded_websites_list.append(new_link)
    description_list.append(description)
    freeness_list.append(freeness)
    tags_list_of_lists.append(tags)
    
    # Use the imported `datetime` object directly
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    datetime_list.append(current_datetime)
    status_list.append("pending") # NEW: Add 'pending' status
    views_list.append("0") # NEW: Add '0' views

    # Re-join the lists and update the DataFrame
    df.loc[user_index, 'uploaded_websites'] = ','.join(uploaded_websites_list)
    df.loc[user_index, 'description'] = ','.join(description_list)
    df.loc[user_index, 'freeness'] = ','.join(freeness_list)
    df.loc[user_index, 'tags'] = '~'.join([json.dumps(t) for t in tags_list_of_lists])
    df.loc[user_index, 'uploaded_datetime'] = ','.join(datetime_list)
    df.loc[user_index, 'status'] = ','.join(status_list) # NEW: Update status column
    df.loc[user_index, 'views'] = ','.join(views_list) # NEW: Update views column
    
    update_sheet_and_clear_cache(df, sheet)
    return True, "Website added successfully! It is now pending review."

def delete_website(current_user, link_to_delete):
    sheet = get_db()
    if sheet is None: return False, "Database connection failed."
    df = get_dataframe(sheet)
    user_index = df[df["username"] == current_user].index[0]
    
    uploaded_websites_list = [w.strip() for w in str(df.loc[user_index, 'uploaded_websites']).split(',') if w.strip()]
    description_list = [d.strip() for d in str(df.loc[user_index, 'description']).split(',') if d.strip()]
    freeness_list = [f.strip() for f in str(df.loc[user_index, 'freeness']).split(',') if f.strip()]
    
    tags_str = str(df.loc[user_index, 'tags'])
    tags_list_of_lists = [t.strip() for t in tags_str.split('~') if t.strip()]
    
    datetime_list = [dt.strip() for dt in str(df.loc[user_index, 'uploaded_datetime']).split(',') if dt.strip()]
    views_list = [v.strip() for v in str(df.loc[user_index, 'views']).split(',') if v.strip()]
    status_list = [s.strip() for s in str(df.loc[user_index, 'status']).split(',') if s.strip()]

    if link_to_delete in uploaded_websites_list:
        link_index = uploaded_websites_list.index(link_to_delete)
        
        uploaded_websites_list.pop(link_index)
        
        if link_index < len(description_list): description_list.pop(link_index)
        if link_index < len(freeness_list): freeness_list.pop(link_index)
        if link_index < len(tags_list_of_lists): tags_list_of_lists.pop(link_index)
        if link_index < len(datetime_list): datetime_list.pop(link_index)
        if link_index < len(views_list): views_list.pop(link_index)
        if link_index < len(status_list): status_list.pop(link_index)

        df.loc[user_index, 'uploaded_websites'] = ','.join(uploaded_websites_list)
        df.loc[user_index, 'description'] = ','.join(description_list)
        df.loc[user_index, 'freeness'] = ','.join(freeness_list)
        df.loc[user_index, 'tags'] = '~'.join(tags_list_of_lists)
        df.loc[user_index, 'uploaded_datetime'] = ','.join(datetime_list)
        df.loc[user_index, 'views'] = ','.join(views_list)
        df.loc[user_index, 'status'] = ','.join(status_list)

        update_sheet_and_clear_cache(df, sheet)
        return True, "Website deleted successfully!"
    return False, "Website not found in your list."

def get_all_website_data(df, include_all=False):
    """
    Processes the DataFrame and returns lists of all website data.
    Safely handles potential data corruption and missing values.
    
    Args:
        df (DataFrame): The DataFrame containing user and website data.
        include_all (bool): If True, returns all websites regardless of status.
                            If False, only returns 'approved' websites.
    """
    if df.empty:
        return [], [], [], [], [], [], [], []

    all_links = []
    all_descriptions = []
    all_freeness = []
    all_tags = []
    all_dates = []
    all_usernames = []
    all_status = []

    for index, row in df.iterrows():
        # Safely get and split string-based columns
        links = [w.strip() for w in str(row.get('uploaded_websites', '')).split(',') if w.strip()]
        descriptions = [d.strip() for d in str(row.get('description', '')).split(',') if d.strip()]
        freeness = [f.strip() for f in str(row.get('freeness', '')).split(',') if f.strip()]
        dates = [dt.strip() for dt in str(row.get('uploaded_datetime', '')).split(',') if dt.strip()]
        status = [s.strip() for s in str(row.get('status', '')).split(',') if s.strip()]

        # Correctly handle tags as lists of lists
        tags_str = str(row.get('tags', '')).strip()
        tags = []
        if tags_str and tags_str.lower() != 'nan':
            for tag_list_str in tags_str.split('~'):
                try:
                    tags.append(json.loads(tag_list_str))
                except (json.JSONDecodeError, TypeError):
                    st.warning(f"Corrupted tag data for user {row.get('username')}.")
                    tags.append([])

        # Align all lists based on the length of the 'links' list
        num_websites = len(links)
        descriptions.extend([None] * (num_websites - len(descriptions)))
        freeness.extend([None] * (num_websites - len(freeness)))
        tags.extend([None] * (num_websites - len(tags)))
        dates.extend([None] * (num_websites - len(dates)))
        status.extend(['pending'] * (num_websites - len(status)))
        
        # Append the data to the main lists, applying the filter
        for i in range(num_websites):
            if include_all or status[i] == 'approved':
                all_links.append(links[i])
                all_descriptions.append(descriptions[i])
                all_freeness.append(freeness[i])
                all_tags.append(tags[i])
                all_dates.append(dates[i])
                all_usernames.append(row['username'])
                all_status.append(status[i])
            
    return all_links, all_descriptions, all_freeness, all_tags, all_dates, all_usernames, all_status


#rendering & search 

def search_websites(query):
    query = query.lower()
    filtered_websites = []
    # Loop through websites with their index
    for i, website_name in enumerate(websites):
        # **Add a check to ensure website_name is not None**
        if website_name is not None:
            if (query in website_name.lower() or
                # Ensure descriptions and tags are not None before accessing
                (i < len(website_descriptions) and website_descriptions[i] is not None and query in website_descriptions[i].lower()) or
                (i < len(website_tags) and website_tags[i] is not None and any(query in tag.lower() for tag in website_tags[i]))):
                
                filtered_websites.append(website_name)
    return filtered_websites
def filter_by_all_tags(websites, website_tags, tags_to_filter):
    """
    Filters a list of websites to return only those that contain all of the specified tags.

    Args:
        websites (list): A list of website names (e.g., ["example.com", "test.net"]).
        website_tags (list): A list of lists, where each inner list contains tags for a corresponding website.
        tags_to_filter (list): The list of tags that all returned websites must have.

    Returns:
        list: A new list of websites that match the filtering criteria.
    """
    if not tags_to_filter:
        return websites
    
    # Convert tags to lowercase and sets for efficient lookup
    tags_to_filter_lower = {tag.lower() for tag in tags_to_filter}
    
    filtered_websites = []
    
    for i, tags_list in enumerate(website_tags):
        # Convert website's tags to a lowercase set
        if tags_list is not None:
            website_tags_lower_set = {tag.lower() for tag in tags_list}
            
            # Check if all of the tags to filter are present in the website's tags
            if tags_to_filter_lower.issubset(website_tags_lower_set):
                filtered_websites.append(websites[i])
            
    return filtered_websites
def sort_website_data(website_links, descriptions, freeness, tags, dates):
    """
    Sorts lists of website data from most recent to oldest based on their dates.

    Args:
        website_links (list): A list of website URLs.
        descriptions (list): A list of website descriptions.
        freeness (list): A list indicating the freeness of websites.
        tags (list): A list of website tags.
        dates (list): A list of datetime formatted strings representing the creation dates.

    Returns:
        tuple: A tuple containing the sorted lists in the order:
                (sorted_website_links, sorted_descriptions, sorted_freeness, sorted_tags, sorted_dates)
    """

    # Check if all lists are of the same length to ensure they can be sorted together
    if not (len(website_links) == len(descriptions) == len(freeness) == len(tags) == len(dates)):
        print("Error: The provided lists are not of the same length.")
        return tuple(None for _ in range(5))

    # Combine all data into a list of tuples, where each tuple contains the date and its corresponding data from other lists
    combined_data = []
    for i in range(len(dates)):
        # Parse the datetime string into a datetime object for proper comparison
        try:
            date_obj = datetime.strptime(dates[i], "%Y-%m-%d %H:%M:%S")
            combined_data.append((date_obj, website_links[i], descriptions[i], freeness[i], tags[i], dates[i]))
        except (ValueError, TypeError) as e:
            print(f"Error parsing date string: {dates[i]}. Skipping this entry. Error: {e}")
            continue

    # Sort the combined data based on the datetime objects (the first element of each tuple) in descending order (most recent to oldest)
    sorted_combined_data = sorted(combined_data, key=lambda x: x[0], reverse=True)

    # Unpack the sorted data back into separate lists
    sorted_dates = [item[5] for item in sorted_combined_data]
    sorted_website_links = [item[1] for item in sorted_combined_data]
    sorted_descriptions = [item[2] for item in sorted_combined_data]
    sorted_freeness = [item[3] for item in sorted_combined_data]
    sorted_tags = [item[4] for item in sorted_combined_data]

    return sorted_website_links, sorted_descriptions, sorted_freeness, sorted_tags, sorted_dates

@st.cache_data
def fetch_favicon_data(url):
    """A helper function to fetch a single favicon."""
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200 and response.content:
            return response.content
    except requests.exceptions.RequestException:
        pass
    return None

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def render_websites(columns, renders):
    """
    Renders websites in batches of 30 with a "Load more" button.
    """
    if "rendered_count" not in st.session_state:
        st.session_state.rendered_count = 21
    
    lottie_url = "https://lottie.host/ac21f009-8b83-4410-92a3-bc638eeaa2fe/Jo9zjjFbdI.json"
    load_anm = load_lottieurl(lottie_url)
    items = len(renders)

    # 1. Prepare a list of URLs for the current batch to fetch
    batch_to_render = renders[:st.session_state.rendered_count]
    urls_to_fetch = [f"https://icons.duckduckgo.com/ip3/{name}.ico" for name in batch_to_render]

    # 2. Fetch all favicons concurrently for the current batch
    if batch_to_render:
        placeholder = st.empty()
        with placeholder:
            left_col, center_col, right_col = st.columns([2, 2, 1.5]) 
            with center_col:
                st_lottie(load_anm, speed=1, reverse=False, loop=True, quality="high", height=400, width=400, key="loading_anim")

        fetched_data = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(fetch_favicon_data, urls_to_fetch)
            for url, data in zip(urls_to_fetch, results):
                fetched_data[url] = data
        placeholder.empty()

    # 3. Render the current batch of results
    if batch_to_render:
        for i in range(0, len(batch_to_render), columns):
            cols = st.columns(columns)
            for j in range(columns):
                current_index = i + j
                if current_index < len(batch_to_render):
                    website_name = batch_to_render[current_index]
                    original_index = websites.index(website_name)

                    duck_url = f"https://icons.duckduckgo.com/ip3/{website_name}.ico"
                    google_url = f"https://www.google.com/s2/favicons?domain={website_name}"

                    with cols[j].container(border=True):
                        if fetched_data.get(duck_url):
                            st.image(fetched_data[duck_url], use_container_width=True)
                        else:
                            st.image(google_url, use_container_width=True)
                        
                        if st.button(website_name, help=f"{website_descriptions[original_index]} {website_freeness[original_index]}", use_container_width=True):
                            components.html(
                                f"""
                                <script>
                                    window.open('https://{website_name}', '_blank');
                                </script>
                                """,
                                height=0,
                                width=0
                            )
                            st.toast("Blocked? Change your settings to allow pop ups for this website.")

    # 4. "Load more" button logic
    if st.session_state.rendered_count < items:
        if st.button("Load more", width='stretch'):
            st.session_state.rendered_count += 21
            st.rerun()

#adding user websites
sheet = get_db()
df = get_dataframe(sheet)
website_links2, descriptions2, freeness2, tags2, dates2, usernames2, status2 = get_all_website_data(df)
websites = website_links2 if isinstance(website_links2, list) else []
website_descriptions = descriptions2 if isinstance(website_descriptions, list) else []
website_freeness = freeness2 if isinstance(freeness2, list) else []
website_tags = tags2 if isinstance(tags2, list) else []
website_dates = dates2 if isinstance(dates2, list) else []

# Sidebar navigation
sheet = get_db()
df = get_dataframe(sheet) if sheet is not None else pd.DataFrame()

with st.sidebar:
    # Adjust the column widths as needed. [1, 1] gives two equally wide columns
    col1, col2 = st.columns([1, 1]) 
    
    with col1:
        st.title("Aixient")
    
    with col2:
        st.markdown(
            f"""
            <div style="margin-top: 10px;">
                <img src="https://avatars.githubusercontent.com/u/36308163?s=200&v=4" width="50">
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    st.markdown("---")
if not st.session_state.logged_in:
    if st.sidebar.button("Sign in", width="stretch"): st.session_state.page = "Sign in"; st.session_state.viewing_profile = None
else:
    if st.session_state.username == ADMIN_USERNAME:
        if st.sidebar.button("Admin Panel", width="stretch"):
            st.session_state.page = "admin_panel"
            st.session_state.viewing_profile = None
    if st.sidebar.button("Profile", width="stretch"):
        st.session_state.page = "profile"
        st.session_state.viewing_profile = None
    if st.sidebar.button("Favorites", width="stretch"):
        st.session_state.page = "favorites"
        st.session_state.viewing_profile = None

if st.sidebar.button("Home", width="stretch"):
    st.session_state.page = "home"
    st.session_state.viewing_profile = None
if st.sidebar.button("Recent", width="stretch"):
    st.session_state.page = "recent"
    st.session_state.viewing_profile = None
if st.sidebar.button("About/Help", width="stretch"):
    st.session_state.page = "about"
    st.session_state.viewing_profile = None
# Main page content
if st.session_state.page == "profile":

    st.markdown(f'<p class="standard">Welcome, {st.session_state.username}</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Add Website Section
    st.subheader("Add a New Website")
    with st.form("add_website_form"):
        new_link = st.text_input("Website URL:")
        description = st.text_area("Description:")
        freeness = st.radio("Freeness:", ["Completely free.","Has a free tier with limitations.","Has a free tier.","Service-based, not free."])
        tags_selected = st.multiselect("Select Tags:", options=tags)
        st.markdown("""
        # Website Submission Guidelines

        ---

        ## 1. Website Content and Relevance
        -   **Focus on Utility:** Only submit websites that provide a specific tool, service, or resource. This can include AI tools, design assets, educational platforms, or other useful utilities.
        -   **No Spam or Harmful Content:** Submissions that are malicious, contain spam, or promote illegal activities will be rejected.
        -   **No Personal Websites or Blogs:** Please don't submit personal portfolios, blogs, or simple informational websites that do not offer a tangible tool or service.

        ---

        ## 2. Information Accuracy
        -   **Provide the Full URL:** Enter the full web address, like `example.com`, without `https://` or `www.`.
        -   **Accurate Descriptions:** Write a clear and concise description that accurately explains what the tool does. A good description is crucial for helping users understand the website's purpose.
        -   **Correct Freeness Level:** Select the option that best describes the cost of the website. This helps users filter for tools that match their budget.
        -   **Tagging:** Choose relevant tags from the provided list that accurately categorize the tool. Tags are essential for search and filtering. You can select multiple tags.

        ---

        ## 3. User Responsibility
        -   **One Submission at a Time:** Ensure you are not submitting the same website multiple times. The system is designed to notify you if the website you're adding already exists in your list.
        -   **Ownership:** You are responsible for the websites you submit. If a submission is found to violate these guidelines, it may be removed.

        ---

        By following these guidelines, you help us keep Aixient a valuable and reliable resource for everyone.
        """)
        add_button = st.form_submit_button("Add Website")

        if add_button:
            if new_link and description:
                success, message = add_website(st.session_state.username, new_link.strip(), description, freeness, tags_selected)
                if success:
                    st.success(message)
                else:
                    st.warning(message)
            else:
                st.error("Please fill in the website URL and description.")
            st.rerun()

    st.markdown("---")
    
    # Display and Manage Websites Section
    st.subheader("Your Uploaded Websites")
    if not df.empty and st.session_state.username in df["username"].values:
        current_user_data = df[df["username"] == st.session_state.username].iloc[0]
        
        websites = [w.strip() for w in str(current_user_data['uploaded_websites']).split(',') if w.strip()]
        descriptions = [d.strip() for d in str(current_user_data['description']).split(',') if d.strip()]
        freeness_levels = [f.strip() for f in str(current_user_data['freeness']).split(',') if f.strip()]
        tags_str_list = [t.strip() for t in str(current_user_data['tags']).split('~') if t.strip()]
        datetimes = [dt.strip() for dt in str(current_user_data['uploaded_datetime']).split(',') if dt.strip()]
        views_list = [v.strip() for v in str(current_user_data['views']).split(',') if v.strip()]
        status_list = [s.strip() for s in str(current_user_data['status']).split(',') if s.strip()]

        if websites:
            for i, link in enumerate(websites):
                with st.container(border=True):
                    st.markdown(f"**URL:** [{link}]({link})")
                    if i < len(descriptions): st.write(f"**Description:** {descriptions[i]}")
                    if i < len(freeness_levels): st.write(f"**Freeness:** {freeness_levels[i]}")
                    if i < len(tags_str_list): st.write(f"**Tags:** {tags_str_list[i]}")
                    if i < len(datetimes): st.write(f"**Uploaded On:** {datetimes[i]}")
                    if i < len(views_list): st.write(f"**Views:** {views_list[i]}")
                    if i < len(status_list): st.write(f"**Status:** {status_list[i].capitalize()}")

                    if st.button("Delete", key=f"delete_{link}"):
                        success, message = delete_website(st.session_state.username, link)
                        if success: st.success(message)
                        else: st.error(message)
                        st.rerun()
        else:
            st.info("You haven't uploaded any websites yet.")
    else:
        st.info("No user data found. Please log in or create an account.")
    if st.button("Logout", width="stretch"):
        st.session_state.logged_in = False
        st.session_state.username = "guest"
        st.session_state.page = "home"
        st.session_state.viewing_profile = None
        st.success("You have been logged out.")
        st.rerun()

# NEW ADMIN PANEL PAGE
if st.session_state.page == "admin_panel" and st.session_state.username == ADMIN_USERNAME:
    st.markdown('<p class="standard">Admin Panel</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Pending Submissions")

    # Get all websites, including those not yet approved
    all_links, all_descriptions, all_freeness, all_tags, all_dates, all_usernames, all_status = get_all_website_data(df, include_all=True)

    pending_submissions = [(link, desc, user, i) for i, (link, desc, user, status) in enumerate(zip(all_links, all_descriptions, all_usernames, all_status)) if status == 'pending']

    if pending_submissions:
        for i, (link, desc, user, original_index) in enumerate(pending_submissions):
            with st.container(border=True):
                st.markdown(f"**URL:** {link}")
                st.markdown(f"**Description:** {desc}")
                st.markdown(f"**Submitted by:** {user}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Approve", key=f"approve_{link}_{i}"):
                        user_data = df[df["username"] == user].iloc[0]
                        user_links = [w.strip() for w in str(user_data['uploaded_websites']).split(',') if w.strip()]
                        link_index = user_links.index(link)
                        success, message = update_website_status(user, link, 'approved')
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                        st.rerun()
                with col2:
                    if st.button("Reject", key=f"reject_{link}_{i}"):
                        user_data = df[df["username"] == user].iloc[0]
                        user_links = [w.strip() for w in str(user_data['uploaded_websites']).split(',') if w.strip()]
                        link_index = user_links.index(link)
                        success, message = update_website_status(user, link, 'rejected')
                        if success:
                            st.warning(message)
                        else:
                            st.error(message)
                        st.rerun()
    else:
        st.info("No websites are pending review at this time.")

if st.session_state.page == "profile":

    st.markdown(f'<p class="standard">Welcome, {st.session_state.username}</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Add Website Section
    st.subheader("Add a New Website")
    with st.form("add_website_form"):
        new_link = st.text_input("Website URL:")
        description = st.text_area("Description:")
        freeness = st.radio("Freeness:", ["Completely free.","Has a free tier with limitations.","Has a free tier.","Service-based, not free."])
        tags_selected = st.multiselect("Select Tags:", options=tags)
        st.markdown("""
        # Website Submission Guidelines
        ---
        ## 1. Website Content and Relevance
        - **Focus on Utility:** Only submit websites that provide a specific tool, service, or resource. This can include AI tools, design assets, educational platforms, or other useful utilities.
        - **No Spam or Harmful Content:** Submissions that are malicious, contain spam, or promote illegal activities will be rejected.
        - **No Personal Websites or Blogs:** Please don't submit personal portfolios, blogs, or simple informational websites that do not offer a tangible tool or service.
        ---
        ## 2. Information Accuracy
        - **Provide the Full URL:** Enter the full web address, like `example.com`, without `https://` or `www.`.
        - **Accurate Descriptions:** Write a clear and concise description that accurately explains what the tool does. A good description is crucial for helping users understand the website's purpose.
        - **Correct Freeness Level:** Select the option that best describes the cost of the website. This helps users filter for tools that match their budget.
        - **Tagging:** Choose relevant tags from the provided list that accurately categorize the tool. Tags are essential for search and filtering. You can select multiple tags.
        ---
        ## 3. User Responsibility
        - **One Submission at a Time:** Ensure you are not submitting the same website multiple times. The system is designed to notify you if the website you're adding already exists in your list.
        - **Ownership:** You are responsible for the websites you submit. If a submission is found to violate these guidelines, it may be removed.
        ---
        By following these guidelines, you help us keep Aixient a valuable and reliable resource for everyone.
        """)
        add_button = st.form_submit_button("Add Website")

    if add_button:
        if new_link and description:
            success, message = add_website(st.session_state.username, new_link.strip(), description, freeness, tags_selected)
            if success:
                st.success(message)
            else:
                st.warning(message)
        else:
            st.error("Please fill in the website URL and description.")
        st.rerun()

    st.markdown("---")
    
    # Display and Manage Websites Section
    st.subheader("Your Uploaded Websites")
    if not df.empty and st.session_state.username in df["username"].values:
        current_user_data = df[df["username"] == st.session_state.username].iloc[0]
        
        websites = [w.strip() for w in str(current_user_data['uploaded_websites']).split(',') if w.strip()]
        descriptions = [d.strip() for d in str(current_user_data['description']).split(',') if d.strip()]
        freeness_levels = [f.strip() for f in str(current_user_data['freeness']).split(',') if f.strip()]
        tags_list = [t.strip() for t in str(current_user_data['tags']).split(',') if t.strip()]
        datetimes = [dt.strip() for dt in str(current_user_data['uploaded_datetime']).split(',') if dt.strip()]
        views_list = [v.strip() for v in str(current_user_data['views']).split(',') if v.strip()]

        if websites:
            for i, link in enumerate(websites):
                with st.container(border=True):
                    st.markdown(f"**URL:** [{link}]({link})")
                    if i < len(descriptions): st.write(f"**Description:** {descriptions[i]}")
                    if i < len(freeness_levels): st.write(f"**Freeness:** {freeness_levels[i]}")
                    if i < len(tags_list): st.write(f"**Tags:** {tags_list[i]}")
                    if i < len(datetimes): st.write(f"**Uploaded On:** {datetimes[i]}")
                    if i < len(views_list): st.write(f"**Views:** {views_list[i]}")

                    if st.button("Delete", key=f"delete_{link}"):
                        success, message = delete_website(st.session_state.username, link)
                        if success: st.success(message)
                        else: st.error(message)
                        st.rerun()
        else:
            st.info("You haven't uploaded any websites yet.")
    else:
        st.info("No user data found. Please log in or create an account.")

    if st.button("Logout", width="stretch"):
        st.session_state.logged_in = False
        st.session_state.username = "guest"
        st.session_state.page = "home"
        st.session_state.viewing_profile = None
        st.success("You have been logged out.")
        st.rerun()

if st.session_state.page == "home":
    st.markdown('<p class="title">Aixient</p>', unsafe_allow_html=True)

    st.markdown('<p class="standard">Explore a vast library of free AI, web tools, and simulations</p>', unsafe_allow_html=True)

    search = st.text_input(label='', label_visibility="hidden", placeholder="Search here")
    options = ['AI', 'free-tier', 'creative', 'tools', 'coding', 'development', 'design', 'art', 'education', 'gaming']

    

    eqcols = st.columns([3, 1])
    with eqcols[0]:
        selected_tags_1 = st.segmented_control('selecting common tags:',options, selection_mode="multi",label_visibility="hidden", width='stretch')
    with eqcols[1]:
        selected_tags_2 = st.multiselect('selecting filters', placeholder='select filters...',label_visibility="hidden",width="stretch", options=tags)

    selected_tags = []
    if selected_tags_1:
        selected_tags.extend(selected_tags_1)
    if selected_tags_2:
        selected_tags.extend(selected_tags_2)

    search_results = filter_by_all_tags(search_websites(search), website_tags, selected_tags)

    render_websites(7, search_results)

if st.session_state.page == "Sign in":
    st.subheader("Sign in to your account")
    

    with st.form("sign_in_form"):
            login_username = st.text_input("Username", key="login_username_input")
            login_password = st.text_input("Password", type="password", key="login_password_input")
            
            # This is where the submit button for the form is located
            submit_button = st.form_submit_button("Sign in", width="stretch")
    
    # Create another set of columns for the buttons on the same horizontal leve

    create_account_button = st.button('Create account', width='stretch')
    
    # Handle the form submission logic
    if submit_button:
        if verify_user(login_username, login_password):
            st.session_state.logged_in = True
            st.session_state.username = login_username
            st.session_state.page = "home"
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password.")
            
    # Handle the "Create account" button logic
    if create_account_button:
        st.session_state.page = "Create account"
        st.rerun()

if st.session_state.page == "Create account":
    st.subheader("Create a new account")
    with st.form("create_account_form"):
        new_username = st.text_input("Username", key="new_username_input")
        new_email = st.text_input("Email", key="new_email_input")
        new_password = st.text_input("Password", type="password", key="new_password_input")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password_input")
        create_button = st.form_submit_button("Create Account")

        if create_button:
            # Check if any field is empty
            if not new_username or not new_password or not confirm_password or not new_email:
                st.error("Please fill in all fields.")
            # Check if the email format is valid using regex
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", new_email):
                st.error("Please enter a valid email address.")
            # Check if passwords match
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                # Add the user to your database, including the email
                # Make sure your add_user function is updated to handle the new email parameter
                success, message = add_user(new_username, new_password)
                if success:
                    st.success("Account created successfully! You can now log in.")
                    st.session_state.page = 'Sign in'
                    st.rerun()
                else:
                    st.error(message)

if st.session_state.page == "recent":

    st.markdown('<p class="title">Recent</p>', unsafe_allow_html=True)
    st.markdown('<p class="standard">Explore recently uploaded websites</p>', unsafe_allow_html=True)
    st.markdown('---')
    websites, website_descriptions, website_freeness, website_tags, website_dates = sort_website_data(websites, website_descriptions, website_freeness, website_tags, website_dates)
    render_websites(7, websites)

if st.session_state.page == "about":
    st.title("About")
    st.write("""
Aixient is a free-to-use website that serves as a curated library of useful AI tools, web tools, and games. It's designed as a good-looking, organized platform where users can easily discover new and innovative websites. I (Blue Raven) built the site to solve a problem: finding a single, well-designed place to  a collection of online resources.

Key Features and Purpose:
             
    • Free to Use and Publish: Too many times I've been to a website and seen adds, pay-walls, and fremniums. That's why I made Aixient completely free
                               for users to use and publish their own projects.

    • A Curated Library: Unlike a standard search engine, Aixient aims to be a high-quality, and that means high-quality websites. No more random, irevelent, not-free
                         AI and websites that definitely paid to have their websites listed higher -here on Aixient, everyone has a chance to have their website noticed.
             
    • I developed Aixient for three main reasons: to build my own personal website, to create a valuable resource I felt was missing from the internet, 
                                                  and because it's just, well, cool :D.
""")
    st.write("""
    ### How Aixient Was Created For Free

    Aixient was developed entirely for free by leveraging a suite of open-source and no-cost services. By choosing the right tools, we were able to build a functional and scalable application without incurring any financial costs for the core infrastructure.

    - **Streamlit**: The entire user interface, from the search bar to the website cards, is powered by Streamlit, a free and open-source Python framework. Streamlit allowed us to create a web application using only Python, saving on development time and avoiding licensing fees.
    - **Google Sheets**: Instead of a traditional, expensive database, we use a Google Sheet to store all user data and website information. The app connects to this sheet using the gspread library, making it a simple yet powerful back-end solution that's completely free to use.
    - **Free Services**: We integrate with other free services to enhance the user experience. We use public APIs from DuckDuckGo and Google to fetch website favicons, and we utilize free Lottie animations for a dynamic loading screen.

    By combining these open-source and free resources, Aixient was able to be created, deployed, and maintained at no cost, allowing us to keep the platform free for everyone.
    """)
    st.markdown("---")
    st.title("Help")
    st.write("Common Q&A")
    with st.expander(label="Why does the domain image look like a globe?", ):
        st.write("To get images for the sites, I use favicons (Lil' images with the tab). Sometimes, a website might not have one, there might not be a registered one, etc. So instead of freaking out, it just returns a standard image: the globe")
    with st.expander(label="Are you data-mining me?"):
        st.write("Your probably not asking this question, but I just wanted to add it for all you internet safetey people. The answers no . . . or am I???")
    with st.expander(label="Can I add my own websites?"):
        st.write("Of course! Create an account and bam, you can help promote your website!")
    with st.expander(label="Are you going to keep it free forever?"):
        st.write("Yes, I intend to keep it free forever.")
    with st.expander(label="Will you add more features?"):
        st.write("Of course! I'll keep things updated on my yt channel.")
    with st.expander(label="How are websites approved?"):
        st.write("When you submit a website, it goes into a pending state. It won't be visible to others until I've had a chance to review it and approve it. This helps keep the quality of the list high and ensures there's no spam.")
    with st.expander(label="Do I need to sign up to use the site?"):
        st.write("No, you don't! Anyone can use the search and browse all the approved websites without an account. You only need to sign up if you want to submit your own website or save favorites (a feature that's coming soon!).")
    with st.expander(label="Why is the site sometimes slow?"):
        st.write("The site is hosted on a free platform, which can sometimes have limited resources. Additionally, every time you refresh the page, the app has to fetch the entire list of websites from the Google Sheet, which can take a moment. The goal is to keep it free, which means working within these constraints.")
    with st.expander(label="Where does the data come from?"):
        st.write("The data is crowd-sourced! All the websites you see on Aixient have been submitted by users like you. I just handle the review process to make sure everything is legitimate and relevant.")
    with st.expander(label="What's the best way to contact you?"):
        st.write("For now, the best way to get updates and send feedback is through my YouTube channel, which I keep updated on new features and other developments.")

if st.session_state.page == "favorites":
    st.write("Not a feature . . . Yet . . . ❤️👁️‍🗨️⭐🔥")