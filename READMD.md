# Image Dataset Visualization Tool

A Streamlit application for visualizing and comparing image datasets across countries and categories.

## Overview

This tool provides an interactive interface to explore and compare four image datasets:

-   **Google Crawled Data (GSCD)**: Raw images collected through web crawling
-   **High Quality Data (HQCD)**: Filtered high-quality images from GSCD
-   **Negative Images**: Images filtered out from GSCD during quality assessment
-   **CCUB Dataset**: Curated country-category dataset with captions

## Installation

### Requirements

-   Python 3.7 or higher
-   Streamlit
-   Pandas
-   Pillow
-   Requests

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install dependencies:

```bash
pip install streamlit pandas pillow requests
```

3. Ensure your dataset structure follows the pattern:

```
data/
├── GSCD/
│   ├── china/
│   │   ├── architecture.csv
│   │   ├── city.csv
│   │   └── ...
│   ├── korea/
│   └── ...
├── HQCD(Country/Category)/
│   ├── china/
│   │   ├── architecture.csv
│   │   └── ...
│   └── ...
├── filter_negative/
│   ├── china/
│   │   ├── architecture.csv
│   │   └── ...
│   └── ...
└── CCUB/
    └── ccub.csv
```

## Usage

1. Run the application:

```bash
streamlit run app.py
```

2. Select a country from the sidebar dropdown (China, Korea, Nigeria, Mexico, and India are prioritized)

3. Select a category or "ALL" to view all categories

4. Adjust the number of images to display using the slider

5. Switch between tabs to view each dataset:
    - High Quality Images (HQCD)
    - Negative Images (Filtered)
    - Google Crawled Data (GSCD)
    - CCUB Dataset

## Features

-   **Comprehensive Visualization**: View and compare images across four different datasets
-   **Country and Category Selection**: Filter images by country and specific categories
-   **Metadata Display**: Expand to view detailed metadata for each image
-   **Image Caption Display**: Shows captions where available
-   **Dataset Statistics**: Real-time statistics on the number of images in each dataset
-   **Category Distribution**: When viewing "ALL" categories, see the distribution of images across categories

## Dataset Details

### Google Crawled Data (GSCD)

Raw images collected through web crawling, organized by country and category. These images contain the `image_url` field to access the original image.

### High Quality Culutre Data (HQCD)

A subset of GSCD that has passed quality filters. These images include captions and various quality scores.

### Negative Images

Images from GSCD that were filtered out during quality assessment. These are stored in the `filter_negative` directory.

### CCUB Dataset

A curated dataset with standardized category codes (ARCHITECTURE, CITIES, CLOTH, etc.) and detailed captions, stored in a single CSV file.

## Category Mapping

GSCD/HQCD categories map to CCUB categories as follows:

-   "architecture" → "ARCHITECTURE"
-   "city" → "CITIES"
-   "clothing" → "CLOTH"
-   "dance and music and visual arts" → "DANCE"
-   "food and drink" → "FOOD"
-   "nature" → "NATURE"
-   "people and action" → "PEOPLE"
-   "religion and festival" → "RELIGION"
-   "utensil and tool" → "TOOLS"

## Notes

-   Large image sets may take time to load depending on your internet connection
-   Some images may fail to load if their URLs are no longer valid
-   For the best experience, set a reasonable number of images to display using the slider
