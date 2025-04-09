import streamlit as st
import pandas as pd
import csv
from jobspy import scrape_jobs

st.set_page_config(page_title="Job Scraper Demo", layout="wide")
st.title("🧪 Real-Time Job Scraper")

st.write("Search for jobs from multiple job boards using rotating proxies (DataImpulse).")

# Sidebar input
st.sidebar.header("Search Settings")

search_term = st.sidebar.text_input("Search Term", "UI UX -PhD -Master -Head")
location = st.sidebar.text_input("Location", "MA, USA")

platforms = st.sidebar.multiselect(
    "Select Platforms",
    ["indeed", "linkedin", "zip_recruiter", "glassdoor", "google", "bayt", "naukri"],
    default=["indeed", "linkedin"]
)

hours_old = st.sidebar.slider("Maximum job age (in hours)", min_value=1, max_value=168, value=144, step=12)

results_limit = st.sidebar.slider("Max results (optional)", min_value=10, max_value=200, value=50, step=10)

run_scrape = st.sidebar.button("Run Scraper")

if run_scrape:
    st.info("Scraping... please wait 10–30 seconds.")

    try:
        jobs = scrape_jobs(
            site_name=platforms,
            search_term=search_term,
            location=location,
            hours_old=hours_old,
            country_indeed='USA',
            results_wanted=results_limit,
            proxies=["728e225554fb4f209000:a39e3c8afd0b1378@gw.dataimpulse.com:823"],
        )

        st.success(f"✅ Found {len(jobs)} jobs!")
        st.dataframe(jobs)

        csv_button = st.download_button(
            label="Download Results as CSV",
            data=jobs.to_csv(quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False),
            file_name="scraped_jobs.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error occurred: {e}")
