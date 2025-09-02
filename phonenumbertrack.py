import streamlit as st
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium
import time
import random

# Streamlit page setup
st.set_page_config(page_title="Phone Number Tracker", page_icon="📱", layout="centered")

# Initialize session state to store results persistently
if 'results' not in st.session_state:
    st.session_state.results = None

# App title and description
st.title("📱 Phone Number Tracker")
st.markdown("Enter a phone number to get details like country, carrier, and timezone, and see its approximate location on a map.")

# Input field for the phone number
phone_number = st.text_input("Enter a phone number (e.g., +12025550172)")

# Checkbox to enable live tracking simulation
live_tracking = st.checkbox("Simulate Live Tracking (for demonstration purposes)")

# Button to trigger the tracking function
if st.button("Track Phone Number"):
    if not phone_number:
        st.error("Please enter a phone number.")
        st.session_state.results = None  # Clear previous results if input is empty
    else:
        try:
            parsed_number = phonenumbers.parse(phone_number, None)

            # Check if the number is valid
            if not phonenumbers.is_valid_number(parsed_number):
                st.error("Invalid phone number. Please enter a valid number, including the country code.")
                st.session_state.results = None
            else:
                country = geocoder.description_for_number(parsed_number, "en")
                sim_carrier = carrier.name_for_number(parsed_number, "en")
                timezones = timezone.time_zones_for_number(parsed_number)
                
                # Get location details using Nominatim
                geolocator = Nominatim(user_agent="phone_number_tracker_app")
                location = geolocator.geocode(country, timeout=10) if country else None

                # Store all the results in the session state to make them persistent
                st.session_state.results = {
                    "phone_number": phone_number,
                    "country": country,
                    "sim_carrier": sim_carrier,
                    "timezones": timezones,
                    "location": location
                }

        except phonenumbers.NumberParseException as e:
            st.error(f"Error parsing number: {e}. Please ensure the country code is included.")
            st.session_state.results = None
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
            st.session_state.results = None

# This section of code will run and display the stored results on every rerun
if st.session_state.results:
    results = st.session_state.results
    st.success("Number details found!")
    st.write(f"**Number:** {results['phone_number']}")
    st.write(f"**Country/Region:** {results['country'] if results['country'] else 'Unknown'}")
    st.write(f"**Carrier:** {results['sim_carrier'] if results['sim_carrier'] else 'Unknown'}")
    st.write(f"**Timezone(s):** {', '.join(results['timezones']) if results['timezones'] else 'Unknown'}")

    # Display the map if location is available
    if results['location']:
        st.write("### Location Map")
        # If live tracking is enabled, simulate movement
        if live_tracking:
            map_placeholder = st.empty()
            phone_lat, phone_lon = results['location'].latitude, results['location'].longitude

            # Simulate 20 location updates for demonstration
            for _ in range(20):
                phone_lat += random.uniform(-0.0005, 0.0005)
                phone_lon += random.uniform(-0.0005, 0.0005)

                m = folium.Map(location=[phone_lat, phone_lon], zoom_start=12)
                folium.CircleMarker(
                    location=[phone_lat, phone_lon],
                    radius=10,
                    color="red",
                    fill=True,
                    fill_color="red"
                ).add_to(m)

                with map_placeholder:
                    st_folium(m, width=700, height=500)
                
                time.sleep(2)  # Wait 2 seconds before the next update
        else:
            # Display a static map
            m = folium.Map(location=[results['location'].latitude, results['location'].longitude], zoom_start=8)
            folium.Marker(
                [results['location'].latitude, results['location'].longitude],
                tooltip=f"{results['country']} - {results['sim_carrier']}",
            ).add_to(m)
            st_folium(m, width=700, height=500)
    else:
        st.warning("Could not find geographical location for this number.")
