import streamlit as st
import pandas as pd
import os
from PIL import Image
import requests
from io import BytesIO
import math

st.set_page_config(layout="wide", page_title="Image Dataset Visualization")

# Set title
st.title("Image Dataset Visualization")
st.markdown(
    "Compare Google Crawled Data, High Quality Data, Filtered Images, and CCUB Dataset"
)

# Get available countries from directory
available_countries = [
    d for d in os.listdir("data/GSCD") if os.path.isdir(f"data/GSCD/{d}")
]

# Prioritize specific countries
priority_countries = ["china", "korea", "nigeria", "mexico", "india"]
# Filter only available priority countries
priority_available = [
    c for c in priority_countries if c in [c.lower() for c in available_countries]
]
# Get case-sensitive names for priority countries
priority_case_sensitive = [
    c for c in available_countries if c.lower() in priority_available
]
# Get remaining countries
other_countries = [
    c for c in available_countries if c.lower() not in priority_available
]
# Create final ordered list
ordered_countries = priority_case_sensitive + other_countries

# Add country selection dropdown to sidebar
selected_country = st.sidebar.selectbox("Select Country", ordered_countries)

# Get category list for selected country and add "ALL" option
categories = [
    f.replace(".csv", "")
    for f in os.listdir(f"data/GSCD/{selected_country}")
    if f.endswith(".csv")
]
categories = ["ALL"] + categories  # Add ALL option at the beginning
selected_category = st.sidebar.selectbox("Select Category", categories)

# Add filter options to sidebar
st.sidebar.header("Display Options")
img_limit = st.sidebar.slider(
    "Number of images to display", 10, 300, 30, key="img_limit"
)

# Initialize session state for pagination
if "page" not in st.session_state:
    st.session_state.page = 1

# Images per page
IMAGES_PER_PAGE = 12
IMAGES_PER_ROW = 3


# Helper function to get country code
def get_country_code(country):
    country_codes = {
        "china": "CHN",
        "egypt": "EGY",
        "france": "FRA",
        "india": "IND",
        "jordan": "JOR",
        "korea": "KOR",
        "mexico": "MEX",
        "nigeria": "NGA",
        "poland": "POL",
        "united states": "USA",
    }
    return country_codes.get(country.lower())


# Helper function to map GSCD category to CCUB category
def map_to_ccub_category(category):
    category_mapping = {
        "architecture": "ARCHITECTURE",
        "city": "CITIES",
        "clothing": "CLOTH",
        "dance and music and visual arts": "DANCE",
        "food and drink": "FOOD",
        "nature": "NATURE",
        "people and action": "PEOPLE",
        "religion and festival": "RELIGION",
        "utensil and tool": "TOOLS",
    }
    return category_mapping.get(category.lower())


# Reverse mapping from CCUB to GSCD categories
def get_ccub_categories():
    return {
        "ARCHITECTURE": "architecture",
        "CITIES": "city",
        "CLOTH": "clothing",
        "DANCE": "dance and music and visual arts",
        "FOOD": "food and drink",
        "NATURE": "nature",
        "PEOPLE": "people and action",
        "RELIGION": "religion and festival",
        "TOOLS": "utensil and tool",
    }


# Load CCUB data separately (it's a single file for all countries/categories)
@st.cache_data
def load_ccub_data():
    ccub_file = "data/CCUB/ccub.csv"
    if os.path.exists(ccub_file):
        return pd.read_csv(ccub_file)
    return pd.DataFrame()


# Data loading function
@st.cache_data
def load_data(country, category):
    # Initialize data dictionaries
    data = {"gscd": None, "hqcd": None, "negative": None}

    if category == "ALL":
        # Load data for all categories
        gscd_all = []
        hqcd_all = []
        negative_all = []

        for cat in os.listdir(f"data/GSCD/{country}"):
            if cat.endswith(".csv"):
                cat_name = cat.replace(".csv", "")

                # GSCD data
                gscd_file = f"data/GSCD/{country}/{cat}"
                gscd_df = pd.read_csv(gscd_file)
                gscd_df["category"] = cat_name
                gscd_all.append(gscd_df)

                # HQCD data
                hqcd_file = f"data/HQCD(Country/Category)/{country}/{cat}"
                if os.path.exists(hqcd_file):
                    hqcd_df = pd.read_csv(hqcd_file)
                    hqcd_df["category"] = cat_name
                    hqcd_all.append(hqcd_df)

                # Negative data
                negative_file = f"data/filter_negative/{country}/{cat_name}.csv"
                if os.path.exists(negative_file):
                    negative_df = pd.read_csv(negative_file)
                    negative_df["category"] = cat_name
                    negative_all.append(negative_df)

        # Combine all dataframes
        data["gscd"] = pd.concat(gscd_all) if gscd_all else pd.DataFrame()
        data["hqcd"] = pd.concat(hqcd_all) if hqcd_all else pd.DataFrame()
        data["negative"] = pd.concat(negative_all) if negative_all else pd.DataFrame()

    else:
        # GSCD data
        gscd_file = f"data/GSCD/{country}/{category}.csv"
        data["gscd"] = pd.read_csv(gscd_file)
        data["gscd"]["category"] = category

        # HQCD data
        hqcd_file = f"data/HQCD(Country/Category)/{country}/{category}.csv"
        data["hqcd"] = pd.read_csv(hqcd_file)
        data["hqcd"]["category"] = category

        # Filtered data (if exists)
        negative_file = f"data/filter_negative/{country}/{category}.csv"
        if os.path.exists(negative_file):
            data["negative"] = pd.read_csv(negative_file)
            data["negative"]["category"] = category
        else:
            data["negative"] = pd.DataFrame()

    return data


# Function to filter CCUB data
def filter_ccub_data(ccub_df, country, category):
    country_code = get_country_code(country)

    # First filter by country
    filtered_df = (
        ccub_df[ccub_df["country_code"] == country_code]
        if country_code
        else pd.DataFrame()
    )

    # If specific category is selected, filter further
    if category != "ALL" and not filtered_df.empty:
        ccub_category = map_to_ccub_category(category)
        if ccub_category:
            filtered_df = filtered_df[filtered_df["category_code"] == ccub_category]

    return filtered_df


# Function to display images
def display_images(df, url_column, limit=30):
    # If no images to display
    if len(df) == 0:
        st.info(f"No images found.")
        return

    # Display total count
    st.write(f"Showing {min(limit, len(df))} of {len(df)} images")

    # Display images in rows of 3
    for i in range(0, min(limit, len(df)), 3):
        cols = st.columns(3)
        for j in range(3):
            idx = i + j
            if idx < min(limit, len(df)):
                row = df.iloc[idx]
                with cols[j]:
                    url = row[url_column]
                    try:
                        st.image(url, use_container_width=True)
                    except:
                        st.error(f"Failed to load image: {url}")

                    # Display category if showing ALL or for CCUB
                    if "category_code" in row:
                        st.caption(f"Category: {row['category_code']}")
                    elif selected_category == "ALL" and "category" in row:
                        st.caption(f"Category: {row['category']}")

                    # Display caption if available
                    if "caption" in row:
                        st.caption(row["caption"])

                    with st.expander("Metadata"):
                        for col, val in row.items():
                            if col not in [url_column, "caption"]:
                                st.write(f"**{col}:** {val}")


# Load data
data = load_data(selected_country, selected_category)
gscd_df = data["gscd"]
hqcd_df = data["hqcd"]
negative_df = data["negative"]

# Load and filter CCUB data separately
ccub_full_df = load_ccub_data()
ccub_df = filter_ccub_data(ccub_full_df, selected_country, selected_category)

# Display statistics
st.subheader("Dataset Statistics")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Google Crawled Images", len(gscd_df))
with col2:
    st.metric("High Quality Images", len(hqcd_df))
with col3:
    st.metric("Negative Images", len(negative_df))
with col4:
    st.metric("CCUB Dataset", len(ccub_df))

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "High Quality Images",
        "Negative Images (Filtered)",
        "Google Crawled Data",
        "CCUB Dataset",
    ]
)

# Tab 1: HQCD images
with tab1:
    if selected_category == "ALL":
        st.subheader(f"{selected_country} - All High Quality Images")
    else:
        st.subheader(f"{selected_country}/{selected_category} - High Quality Images")

    # Download button for HQCD data
    if not hqcd_df.empty:
        csv_data = hqcd_df.to_csv(index=False).encode("utf-8")
        download_filename = (
            f"{selected_country}_{selected_category}_HQCD.csv"
            if selected_category != "ALL"
            else f"{selected_country}_ALL_HQCD.csv"
        )
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=download_filename,
            mime="text/csv",
        )

    display_images(hqcd_df, "url", img_limit)

# Tab 2: Negative images
with tab2:
    if selected_category == "ALL":
        st.subheader(f"{selected_country} - All Negative Images (Filtered)")
    else:
        st.subheader(
            f"{selected_country}/{selected_category} - Negative Images (Filtered)"
        )

    # Download button for Negative data
    if not negative_df.empty:
        csv_data = negative_df.to_csv(index=False).encode("utf-8")
        download_filename = (
            f"{selected_country}_{selected_category}_Negative.csv"
            if selected_category != "ALL"
            else f"{selected_country}_ALL_Negative.csv"
        )
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=download_filename,
            mime="text/csv",
        )

    display_images(negative_df, "url", img_limit)

# Tab 3: Google Crawled Data
with tab3:
    if selected_category == "ALL":
        st.subheader(f"{selected_country} - All Google Crawled Data")
    else:
        st.subheader(f"{selected_country}/{selected_category} - Google Crawled Data")

    # Download button for GSCD data
    if not gscd_df.empty:
        csv_data = gscd_df.to_csv(index=False).encode("utf-8")
        download_filename = (
            f"{selected_country}_{selected_category}_GSCD.csv"
            if selected_category != "ALL"
            else f"{selected_country}_ALL_GSCD.csv"
        )
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=download_filename,
            mime="text/csv",
        )

    display_images(gscd_df, "image_url", img_limit)

# Tab 4: CCUB Dataset
with tab4:
    if selected_category == "ALL":
        st.subheader(f"{selected_country} - CCUB Dataset")
    else:
        st.subheader(f"{selected_country}/{selected_category} - CCUB Dataset")

    # Download button for CCUB data
    if not ccub_df.empty:
        csv_data = ccub_df.to_csv(index=False).encode("utf-8")
        download_filename = (
            f"{selected_country}_{selected_category}_CCUB.csv"
            if selected_category != "ALL"
            else f"{selected_country}_ALL_CCUB.csv"
        )
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=download_filename,
            mime="text/csv",
        )

    display_images(ccub_df, "url", img_limit)

# Display category distribution if ALL is selected
if selected_category == "ALL":
    st.sidebar.subheader("Category Distribution")

    # HQCD category counts
    if not hqcd_df.empty and "category" in hqcd_df.columns:
        hqcd_counts = hqcd_df["category"].value_counts().sort_index()
        st.sidebar.write("High Quality Images:")
        for cat, count in hqcd_counts.items():
            st.sidebar.write(f"- {cat}: {count}")

    # Negative category counts
    if not negative_df.empty and "category" in negative_df.columns:
        negative_counts = negative_df["category"].value_counts().sort_index()
        st.sidebar.write("Negative Images:")
        for cat, count in negative_counts.items():
            st.sidebar.write(f"- {cat}: {count}")

    # CCUB category counts
    if not ccub_df.empty and "category_code" in ccub_df.columns:
        ccub_counts = ccub_df["category_code"].value_counts().sort_index()
        st.sidebar.write("CCUB Dataset:")
        for cat, count in ccub_counts.items():
            st.sidebar.write(f"- {cat}: {count}")
