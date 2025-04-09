import streamlit as st
import pandas as pd

# Sample data - you can load your real scrape_jobs() output instead
sample_jobs = pd.DataFrame({
    "Title": ["Bioinformatics Intern", "Lab Assistant", "Entry-Level Data Analyst"],
    "Company": ["Genentech", "Harvard Medical", "Moderna"],
    "Location": ["Boston, MA", "Cambridge, MA", "Brookline, MA"],
    "Posted": ["2 days ago", "1 day ago", "3 days ago"],
    "Link": ["https://example.com/job1", "https://example.com/job2", "https://example.com/job3"]
})

st.set_page_config(page_title="Job Scraper Demo", layout="wide")

st.title("🔍 Entry-Level Job Scraper Demo")
st.write("This demo simulates scraping job listings from major platforms like Indeed, LinkedIn, and Glassdoor.")

with st.form("scrape_form"):
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Search term", "bioinformatics")
        platforms = st.multiselect(
            "Choose job platforms",
            ["Indeed", "LinkedIn", "Glassdoor"],
            default=["Indeed"]
        )
    with col2:
        location = st.text_input("Location", "Brookline, MA")
        max_results = st.slider("Results wanted", min_value=10, max_value=100, value=20, step=10)

    submitted = st.form_submit_button("Run Scraper")

if submitted:
    st.success(f"Scraping {max_results} '{search_term}' jobs from {', '.join(platforms)} in {location}...")
    st.info("Note: This is a simulated result for demo purposes.")
    st.dataframe(sample_jobs)
