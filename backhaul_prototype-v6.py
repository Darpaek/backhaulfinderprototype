import streamlit as st
import pandas as pd
import numpy as np
import math
import time
import random
from datetime import datetime, timedelta

# =====================================================================
# Page Configuration & Styling
# =====================================================================
st.set_page_config(
    page_title="Backhaul Finder - Nationwide Pro",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Wow Factor"
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #0f52ba;
        margin-bottom: 10px;
    }
    .load-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #eef2f5;
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .load-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
    }
    .source-dat {
        background-color: #0f52ba;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    .source-lbn {
        background-color: #2ec4b6;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    .source-dfs {
        background-color: #4a5568;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
    .match-score {
        background-color: #2ec4b6;
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
    }
    .stButton>button {
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# Database / Coordinate Mapping (All Continental US Coverage)
# =====================================================================
# Comprehensive 2-digit ZIP prefix coordinates to cover the entire US
US_ZIP_PREFIXES = {
    '01': (42.3601, -71.0589, 'Boston Metro, MA'),
    '02': (42.3601, -71.0589, 'Boston, MA'),
    '03': (43.0718, -70.7626, 'Portsmouth, NH'),
    '04': (43.6615, -70.2553, 'Portland, ME'),
    '05': (44.4756, -73.2121, 'Burlington, VT'),
    '06': (41.7637, -72.6851, 'Hartford, CT'),
    '07': (40.7357, -74.1724, 'Newark, NJ'),
    '08': (40.2170, -74.7429, 'Trenton, NJ'),
    '09': (40.7128, -74.0060, 'NYC Military/Metro, NY'),
    '10': (40.7128, -74.0060, 'New York City, NY'),
    '11': (40.7128, -74.0060, 'Long Island, NY'),
    '12': (42.6526, -73.7562, 'Albany, NY'),
    '13': (43.0481, -76.1474, 'Syracuse, NY'),
    '14': (43.1566, -77.6088, 'Rochester, NY'),
    '15': (40.4406, -79.9959, 'Pittsburgh, PA'),
    '16': (42.1292, -80.0851, 'Erie, PA'),
    '17': (40.2737, -76.8867, 'Harrisburg, PA'),
    '18': (41.4090, -75.6624, 'Scranton, PA'),
    '19': (39.9526, -75.1652, 'Philadelphia, PA'),
    '20': (38.9072, -77.0369, 'Washington, DC'),
    '21': (39.2904, -76.6122, 'Baltimore, MD'),
    '22': (37.5407, -77.4360, 'Richmond, VA'),
    '23': (36.8508, -76.2859, 'Norfolk, VA'),
    '24': (37.2710, -79.9414, 'Roanoke, VA'),
    '25': (38.3498, -81.6326, 'Charleston, WV'),
    '26': (39.2806, -80.3445, 'Clarksburg, WV'),
    '27': (35.7796, -78.6382, 'Raleigh/Durham, NC'),
    '28': (35.2271, -80.8431, 'Charlotte, NC'),
    '29': (34.0007, -81.0348, 'Columbia, SC'),
    '30': (33.7490, -84.3880, 'Atlanta, GA'),
    '31': (32.0809, -81.0912, 'Savannah, GA'),
    '32': (30.3322, -81.6557, 'Jacksonville, FL'),
    '33': (25.7617, -80.1918, 'Miami, FL'),
    '34': (27.9506, -82.4572, 'Tampa, FL'),
    '35': (33.5186, -86.8104, 'Birmingham, AL'),
    '36': (32.3668, -86.3006, 'Montgomery, AL'),
    '37': (36.1627, -86.7816, 'Nashville, TN'),
    '38': (35.1495, -90.0490, 'Memphis, TN'),
    '39': (32.2988, -90.1848, 'Jackson, MS'),
    '40': (38.2527, -85.7585, 'Louisville, KY'),
    '41': (38.0406, -84.5037, 'Lexington, KY'),
    '42': (36.9959, -86.4426, 'Bowling Green, KY'),
    '43': (39.9612, -82.9988, 'Columbus, OH'),
    '44': (41.4993, -81.6944, 'Cleveland, OH'),
    '45': (39.1031, -84.5120, 'Cincinnati, OH'),
    '46': (39.7684, -86.1581, 'Indianapolis, IN'),
    '47': (37.9716, -87.5711, 'Evansville, IN'),
    '48': (42.3314, -83.0458, 'Detroit, MI'),
    '49': (42.9634, -85.6679, 'Grand Rapids, MI'),
    '50': (41.5868, -93.6250, 'Des Moines, IA'),
    '51': (42.4965, -96.4049, 'Sioux City, IA'),
    '52': (42.0083, -91.6441, 'Cedar Rapids, IA'),
    '53': (43.0389, -87.9065, 'Milwaukee, WI'),
    '54': (44.5133, -88.0133, 'Green Bay, WI'),
    '55': (44.9778, -93.2650, 'Minneapolis, MN'),
    '56': (44.0234, -92.4629, 'Rochester, MN'),
    '57': (43.5460, -96.7313, 'Sioux Falls, SD'),
    '58': (46.8083, -100.7837, 'Bismarck, ND'),
    '59': (45.7833, -108.5007, 'Billings, MT'),
    '60': (41.8781, -87.6298, 'Chicago, IL'),
    '61': (42.2711, -89.0940, 'Rockford, IL'),
    '62': (39.7817, -89.6501, 'Springfield, IL'),
    '63': (38.6270, -90.1994, 'St. Louis, MO'),
    '64': (39.0997, -94.5786, 'Kansas City, MO'),
    '65': (38.5767, -92.1735, 'Jefferson City, MO'),
    '66': (39.0558, -95.6890, 'Topeka, KS'),
    '67': (37.6872, -97.3301, 'Wichita, KS'),
    '68': (40.8258, -96.6852, 'Lincoln, NE'),
    '69': (41.8675, -103.6608, 'Scottsbluff, NE'),
    '70': (29.9511, -90.0715, 'New Orleans, LA'),
    '71': (32.5252, -93.7502, 'Shreveport, LA'),
    '72': (34.7465, -92.2896, 'Little Rock, AR'),
    '73': (35.4676, -97.5164, 'Oklahoma City, OK'),
    '74': (36.1540, -95.9928, 'Tulsa, OK'),
    '75': (32.7767, -96.7970, 'Dallas, TX'),
    '76': (32.7555, -97.3308, 'Fort Worth, TX'),
    '77': (29.7604, -95.3698, 'Houston, TX'),
    '78': (29.4241, -98.4936, 'San Antonio, TX'),
    '79': (33.5779, -101.8552, 'Lubbock, TX'),
    '80': (39.7392, -104.9903, 'Denver, CO'),
    '81': (39.0639, -108.5506, 'Grand Junction, CO'),
    '82': (41.1400, -104.8203, 'Cheyenne, WY'),
    '83': (43.6150, -116.2023, 'Boise, ID'),
    '84': (40.7608, -111.8910, 'Salt Lake City, UT'),
    '85': (33.4484, -112.0740, 'Phoenix, AZ'),
    '86': (35.1983, -111.6513, 'Flagstaff, AZ'),
    '87': (35.0844, -106.6511, 'Albuquerque, NM'),
    '88': (32.3123, -106.7784, 'Las Cruces, NM'),
    '89': (36.1716, -115.1398, 'Las Vegas, NV'),
    '90': (34.0522, -118.2437, 'Los Angeles, CA'),
    '91': (34.1425, -118.1430, 'Pasadena, CA'),
    '92': (32.7157, -117.1611, 'San Diego, CA'),
    '93': (35.3733, -119.0187, 'Bakersfield, CA'),
    '94': (37.7749, -122.4194, 'San Francisco, CA'),
    '95': (38.5816, -121.4944, 'Sacramento, CA'),
    '96': (21.3069, -157.8583, 'Honolulu, HI'),
    '97': (45.5152, -122.6784, 'Portland, OR'),
    '98': (47.6062, -122.3321, 'Seattle, WA'),
    '99': (61.2181, -149.9003, 'Anchorage, AK')
}

def resolve_zip_to_coords(zip_str):
    """Robust lookup that converts any 5-digit ZIP to real US coordinates."""
    zip_str = str(zip_str).strip().zfill(5)[:5]
    prefix_2 = zip_str[:2]
    
    if prefix_2 in US_ZIP_PREFIXES:
        lat, lon, city_name = US_ZIP_PREFIXES[prefix_2]
        try:
            # Distort coordinate slightly based on the last 3 digits so nearby ZIPs map differently but group in the same metro
            last_3 = int(zip_str[2:])
            lat_offset = ((last_3 % 100) - 50) / 200.0
            lon_offset = (((last_3 // 10) % 100) - 50) / 200.0
            lat += lat_offset
            lon += lon_offset
        except ValueError:
            pass
        return lat, lon, f"{city_name.split(',')[0]}, {city_name.split(',')[-1].strip()}"
    
    # Fallback to center of United States
    return 39.8283, -98.5795, f"Continental US (ZIP {zip_str})"

def calculate_haversine(lat1, lon1, lat2, lon2):
    """Haversine formula to compute great-circle distance in miles."""
    R = 3958.8  # Earth's radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2)**2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

def find_closest_city_zip(lat, lon):
    """Finds the closest 2-digit ZIP prefix and returns a realistic synthetic ZIP and city name."""
    closest_prefix = '75'
    min_dist = float('inf')
    for prefix, (p_lat, p_lon, p_city) in US_ZIP_PREFIXES.items():
        dist = calculate_haversine(lat, lon, p_lat, p_lon)
        if dist < min_dist:
            min_dist = dist
            closest_prefix = prefix
    
    if closest_prefix:
        p_lat, p_lon, city_name = US_ZIP_PREFIXES[closest_prefix]
        clean_city = f"{city_name.split(',')[0].strip()}, {city_name.split(',')[-1].strip()}"
        # Generate a realistic random 3-digit suffix
        synthetic_zip = f"{closest_prefix}{random.randint(100, 999):03d}"
        return synthetic_zip, clean_city
    return "75201", "Dallas, TX"


# =====================================================================
# Dynamic Load Board Generator (Nationwide Emulation Engine)
# =====================================================================
def generate_matching_backhauls(orig_zip, dest_zip, equip_type, max_dh, max_ret_proximity, strategy, empty_dt):
    """Generates a highly realistic, responsive list of backhauls anywhere in the US."""
    lat_orig, lon_orig, city_orig = resolve_zip_to_coords(orig_zip)
    lat_dest, lon_dest, city_dest = resolve_zip_to_coords(dest_zip)
    
    # Major brokers for simulation
    brokers = [
        {"name": "C.H. Robinson", "phone": "(800) 323-7587"},
        {"name": "Coyote Logistics", "phone": "(877) 626-9683"},
        {"name": "Landstar System", "phone": "(800) 872-9400"},
        {"name": "Echo Global Logistics", "phone": "(800) 354-7993"},
        {"name": "TQL (Total Quality)", "phone": "(800) 580-3101"},
        {"name": "RXO Capacity", "phone": "(800) 243-7053"}
    ]
    
    boards = ["DAT One", "LoadBoard Network (LBN)", "Direct Freight (DFS)"]
    
    # Generate 5 potential matches
    raw_loads = []
    
    # Match 1: Excellent local match (Very low deadhead, exact return match)
    raw_loads.append({
        "dh_factor": 0.15,       # 15% of max deadhead
        "ret_factor": 0.1,       # 10% of max return offset
        "rpm_mult": 1.25,        # 25% premium rate
        "board": "DAT One",
        "notes": "Direct shipper drop & hook, high priority backhaul contract."
    })
    
    # Match 2: Solid balanced match
    raw_loads.append({
        "dh_factor": 0.45,
        "ret_factor": 0.35,
        "rpm_mult": 1.05,
        "board": "LoadBoard Network (LBN)",
        "notes": "No-touch freight. Palletized and shrink-wrapped."
    })
    
    # Match 3: High yield but further away
    raw_loads.append({
        "dh_factor": 0.8,
        "ret_factor": 0.5,
        "rpm_mult": 1.45,        # High paying rate
        "board": "DAT One",
        "notes": "Expedited team transit requested. Clean trailer required."
    })
    
    # Match 4: Cheap, easy local run (Direct Freight)
    raw_loads.append({
        "dh_factor": 0.25,
        "ret_factor": 0.65,
        "rpm_mult": 0.85,        # Lower rate but very simple
        "board": "Direct Freight (DFS)",
        "notes": "Standard backhaul load. Dock release ready."
    })
    
    # Match 5: Borderline match (high deadhead, high return offset)
    raw_loads.append({
        "dh_factor": 0.95,
        "ret_factor": 0.9,
        "rpm_mult": 0.95,
        "board": "LoadBoard Network (LBN)",
        "notes": "Multi-stop delivery. Driver assist required."
    })
    
    matched_results = []
    
    for i, config in enumerate(raw_loads):
        broker = random.choice(brokers)
        
        # Calculate matching coordinates based on limits
        actual_dh = max_dh * config["dh_factor"]
        # Add random bearing
        angle_dh = random.uniform(0, 2 * math.pi)
        lat_load_orig = lat_orig + (actual_dh / 69.0) * math.sin(angle_dh)
        lon_load_orig = lon_orig + (actual_dh / (69.0 * math.cos(math.radians(lat_orig)))) * math.cos(angle_dh)
        
        actual_ret = max_ret_proximity * config["ret_factor"]
        angle_ret = random.uniform(0, 2 * math.pi)
        lat_load_dest = lat_dest + (actual_ret / 69.0) * math.sin(angle_ret)
        lon_load_dest = lon_dest + (actual_ret / (69.0 * math.cos(math.radians(lat_dest)))) * math.cos(angle_ret)
        
        # Calculate haul distance between the load's start and end coordinates
        haul_miles = calculate_haversine(lat_load_orig, lon_load_orig, lat_load_dest, lon_load_dest)
        
        # If the haul is ridiculously short, scale it up realistically
        if haul_miles < 20.0:
            haul_miles = calculate_haversine(lat_orig, lat_dest) * (1 - config["dh_factor"]*0.1)
            haul_miles = max(round(haul_miles), 45.0)
            
        # Re-verify exact deadhead and return offsets
        precise_dh = calculate_haversine(lat_orig, lon_orig, lat_load_orig, lon_load_orig)
        precise_ret = calculate_haversine(lat_load_dest, lon_load_dest, lat_dest, lon_dest)
        
        # Payout rates based on equipment type
        base_rate = 2.10 if equip_type == "Reefer" else 1.85
        rate_per_mile = round(base_rate * config["rpm_mult"], 2)
        total_rate = round(haul_miles * rate_per_mile)
        
        # Find closest cities and realistic zips based on the actual load coordinates
        f_orig_zip, l_city_orig = find_closest_city_zip(lat_load_orig, lon_load_orig)
        f_dest_zip, l_city_dest = find_closest_city_zip(lat_load_dest, lon_load_dest)
        
        # Timing & Layover Math
        # Generate a random layover (hours and minutes)
        layover_hours = random.randint(1, 24)
        layover_minutes = random.choice([0, 15, 30, 45])
        
        pickup_dt = empty_dt + timedelta(hours=layover_hours, minutes=layover_minutes)
        layover_str = f"{layover_hours:02d}:{layover_minutes:02d}"
        
        # Heuristic scoring
        dh_penalty = min(precise_dh * 0.5, 30)
        ret_penalty = min(precise_ret * 0.5, 30)
        score = max(100 - (dh_penalty + ret_penalty), 20)
        
        # Optimization strategies adjustments
        if strategy == "Max Hourly Yield ($/hr)":
            score = min(score + (rate_per_mile * 6), 100)
        elif strategy == "Minimize Total Empty Miles":
            score = max(score - (precise_dh * 0.9), 10)
            
        # Compile match card details
        matched_results.append({
            "id": f"{config['board'][:3].upper()}-{random.randint(400, 999)}",
            "source": config["board"],
            "market_origin": city_orig,
            "market_dest": city_dest,
            "origin": l_city_orig,
            "origin_zip": f_orig_zip,
            "dest": l_city_dest,
            "dest_zip": f_dest_zip,
            "deadhead": round(precise_dh, 1),
            "haul_miles": round(haul_miles, 1),
            "return_proximity": round(precise_ret, 1),
            "pickup_time": pickup_dt.strftime("%Y-%m-%d %H:%M"),
            "layover": layover_str,
            "rate": total_rate,
            "rpm": rate_per_mile,
            "score": round(score),
            "broker": broker["name"],
            "contact": broker["phone"],
            "notes": config["notes"]
        })
        
    return sorted(matched_results, key=lambda x: x["score"], reverse=True)

# =====================================================================
# Authentication Security Barrier
# =====================================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_login():
    """Simple prototype credential check"""
    if st.session_state.user == "admin" and st.session_state.password == "backhaul2026":
        st.session_state.authenticated = True
        st.success("Login Successful!")
        st.rerun()
    else:
        st.error("Incorrect credentials. For testing, use admin / backhaul2026")

# =====================================================================
# Login Screen Visuals
# =====================================================================
if not st.session_state.authenticated:
    st.title("🚚 US Operations - Backhaul Finder (Nationwide)")
    st.write("Welcome! This is an interactive portal designed for US Operations dispatch to instantly optimize return legs anywhere in the US.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("Login Form"):
            st.subheader("🔑 Operations Portal Login")
            st.text_input("Username", key="user", value="admin")
            st.text_input("Password", type="password", key="password", value="backhaul2026")
            st.form_submit_button("Log In", on_click=check_login)
            st.info("💡 **Prototype Mode Active:** Feel free to log in with pre-filled credentials.")
    st.stop()

# =====================================================================
# Main Application Dashboard (Post-Login)
# =====================================================================
# Sidebar Options
st.sidebar.title("🛠️ Optimization Control")
st.sidebar.markdown("Configure search radius parameters and priority weighting below.")

max_deadhead = st.sidebar.slider("Max Deadhead Radius (miles)", 10, 250, 100, step=10)
max_return_dist = st.sidebar.slider("Max Return Zip Radius (miles)", 10, 250, 100, step=10)
timing_priority = st.sidebar.radio("Optimization Strategy", ["Balanced Criteria", "Max Hourly Yield ($/hr)", "Minimize Total Empty Miles"])

if st.sidebar.button("🔓 Log Out"):
    st.session_state.authenticated = False
    st.rerun()

# Header block
st.title("🚀 Backhaul Finder: Intelligent Matching Engine")
st.write("US Operations & Dispatch Control Panel — **Continental US Emulation Active**")

# Inputs Container
with st.container():
    st.subheader("📍 Step 1: Tractor Availability Input")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delivery_zip = st.text_input("Tractor Delivery ZIP Code", value="75201", help="Enter ANY valid US ZIP code.")
    with col2:
        delivery_date = st.date_input("Delivery Completion Date", datetime.today().date())
    with col3:
        delivery_time = st.time_input("Tractor Empty Time", value=datetime.strptime("08:00", "%H:%M").time())
    with col4:
        trailer_status = st.selectbox("Trailer Status", ["Has Empty Company Trailer", "Power Only (No Trailer)"])

    col1_r, col2_r, col3_r, col4_r = st.columns(4)
    with col1_r:
        return_zip = st.text_input("Ideal Return ZIP Code", value="17404", help="Enter ANY valid US ZIP code.")
    with col2_r:
        return_date = st.date_input("Target Return Date", (datetime.today() + timedelta(days=1)).date())
    with col3_r:
        return_time = st.time_input("Target Return Time", value=datetime.strptime("17:00", "%H:%M").time())
    with col4_r:
        equipment_type = st.selectbox("Equipment Type Match", ["Dry Van", "Reefer"])

# Combine inputs into empty datetime for timing calculations
empty_dt = datetime.combine(delivery_date, delivery_time)

# Matching Execution Section
st.write("---")
if st.button("🔍 Run Live Match Engine", type="primary"):
    with st.spinner("🔄 API Gateways Active: Querying nationwide REST endpoints..."):
        
        # Simulating external API search latency
        time.sleep(1.4)
        
        # Get coordinates for display validation
        try:
            _, _, c_orig = resolve_zip_to_coords(delivery_zip)
            _, _, c_dest = resolve_zip_to_coords(return_zip)
            st.success(f"📍 GPS Reference Locked: **{c_orig}** ➔ **{c_dest}**")
        except Exception:
            st.error("Invalid ZIP format. Please use a standard 5-digit code.")
            st.stop()
            
        # Run matching engine with the empty_dt passed in
        matched_results = generate_matching_backhauls(
            delivery_zip, 
            return_zip, 
            equipment_type, 
            max_deadhead, 
            max_return_dist, 
            timing_priority,
            empty_dt
        )
        
        # Present Results
        st.subheader("🎯 Real-Time Match Engine Output")
        
        # Top-line metrics row
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric(label="Total API Feeds Queried", value="3 (DAT, LBN, DFS)")
        with m2:
            st.metric(label="Raw Postings Swept", value="1,842 Loads")
        with m3:
            st.metric(label="Matches meeting Radius limits", value=len(matched_results))
        with m4:
            st.metric(label="Highest Match Alignment", value=f"{matched_results[0]['score']}%" if matched_results else "0%")
            
        if not matched_results:
            st.warning("⚠️ No matches found under your current search parameters. Try expanding your search radius sliders in the sidebar.")
        else:
            # Display matching cards
            for res in matched_results:
                with st.container():
                    # Check board styles
                    if "DAT" in res["source"]:
                        source_class = "source-dat"
                    elif "LBN" in res["source"]:
                        source_class = "source-lbn"
                    else:
                        source_class = "source-dfs"
                        
                    st.markdown(f"""
                    <div class="load-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                            <div>
                                <span class="{source_class}">{res["source"].upper()} FEED</span>
                                <span style="font-weight: bold; font-size: 14px; margin-left: 10px; color:#555;">ID: {res["id"]}</span>
                            </div>
                            <div>
                                <span class="match-score">Match Score: {res["score"]}%</span>
                            </div>
                        </div>
                        <div style="display: flex; flex-wrap: wrap; margin-bottom: 10px;">
                            <div style="flex: 1.5; min-width: 250px;">
                                <h4 style="margin:0; color:#1a202c; font-size: 18px;">🗺️ {res["market_origin"]} ➔ {res["market_dest"]}</h4>
                                <p style="margin:6px 0 0 0; color:#4a5568; font-size:14px;">
                                    <b>Expected Pickup Window:</b> {res["pickup_time"]}<br/>
                                    <b>Locked Equipment Type:</b> {equipment_type}
                                </p>
                            </div>
                            <div style="flex: 1.3; min-width: 200px; border-left: 1px solid #edf2f7; padding-left: 15px;">
                                <p style="margin:0; color:#4a5568; font-size:14px; line-height: 1.5;">
                                    <b>Route:</b> {res["origin"]} ({res["origin_zip"]}) ➔ {res["dest"]} ({res["dest_zip"]})<br/>
                                    <b>Calculated Deadhead:</b> <span style="color:#e53e3e; font-weight:bold;">{res["deadhead"]} mi</span><br/>
                                    <b>Route Haul Miles:</b> <b>{res["haul_miles"]} mi</b><br/>
                                    <b>Return Offset:</b> <b>{res["return_proximity"]} mi</b><br/>
                                    <b>Layover:</b> <span style="color:#2b6cb0; font-weight:bold;">{res["layover"]} hr</span>
                                </p>
                            </div>
                            <div style="flex: 1; min-width: 150px; border-left: 1px solid #edf2f7; padding-left: 15px;">
                                <p style="margin:0; color:#2f855a; font-size: 20px; font-weight: bold;">
                                    ${res["rate"]:,.2f}
                                </p>
                                <p style="margin: 2px 0 0 0; color: #718096; font-size:13px;">
                                    (${res["rpm"]}/mile yield)
                                </p>
                            </div>
                            <div style="flex: 1.2; min-width: 200px; border-left: 1px solid #edf2f7; padding-left: 15px;">
                                <p style="margin:0; color:#2d3748; font-size:13px;">
                                    <b>Broker:</b> {res["broker"]}<br/>
                                    <b>Contact Support:</b> <a href="tel:{res["contact"]}" style="color:#0f52ba; text-decoration:none; font-weight:bold;">{res["contact"]}</a><br/>
                                    <span style="display:inline-block; margin-top:5px; background-color:#f7fafc; padding:3px 6px; border-radius:4px; font-style:italic; font-size:11px; color:#4a5568;">
                                        "{res["notes"]}"
                                    </span>
                                </p>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px;">
                            <button style="background-color: #f7fafc; color: #4a5568; border: 1px solid #cbd5e0; padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: bold; cursor: pointer;">
                                📞 Call Broker
                            </button>
                            <button style="background-color: #0f52ba; color: white; border: none; padding: 6px 14px; border-radius: 6px; font-size: 13px; font-weight: bold; cursor: pointer;">
                                ⚡ Instant Book
                            </button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Export CSV capability
            df_export = pd.DataFrame(matched_results)
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Optimized Matches to CSV Spreadsheet",
                data=csv,
                file_name=f"Backhaul_Matches_{delivery_zip}_to_{return_zip}.csv",
                mime="text/csv"
            )
