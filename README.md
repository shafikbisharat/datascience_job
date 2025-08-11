# Data Science Jobs Scraper and Dashboard

[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/shafikbisharat/datascience_job/scrape.yml?branch=main)](https://github.com/shafikbisharat/datascience_job/actions)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

🔗 **Live Dashboard:**  
[https://shafikbisharat.github.io/datascience_job/jobs_dashboard.html](https://shafikbisharat.github.io/datascience_job/jobs_dashboard.html)

---

## 1. Scraper / Crawler

The project features a Python-based scraper (`scraper.py`) that collects data science job postings in Israel from leading job platforms — primarily **LinkedIn** and **Google Careers**. It sends HTTP requests simulating real browsers (with randomized user agents), parses HTML pages using BeautifulSoup, and extracts structured job information such as:

- Job title  
- Company name  
- Location  
- Posting date  
- Job URL  

The scraper supports pagination (for LinkedIn), rate limiting retries, and ensures no duplicated job entries by checking unique job links. The collected jobs are saved into a CSV file (`Data_Science_Jobs_Israel.csv`), which serves as the data source for the dashboard.

---

## 2. Automation

The scraping and dashboard generation are fully automated via **GitHub Actions** workflows. Every 12 hours, the workflow runs the scraper, merges new jobs with existing data, and then generates an interactive, standalone HTML dashboard summarizing the latest job market data. This dashboard is committed and pushed back to the repository automatically.

This automation provides a seamless, up-to-date data pipeline from web scraping to visualization without any manual intervention.

---

## 3. Data Sources and Dashboard Creation

### Data Sources

Data is primarily sourced from:

- **LinkedIn:** The scraper navigates LinkedIn job search pages filtered for data scientist roles in Israel, extracting comprehensive listings while respecting pagination and rate limits.

- **Google Careers:** Job postings labeled for data scientist positions within Israel are scraped and parsed similarly.

These two platforms collectively cover a broad range of data science job opportunities.

### Dashboard Generation

The dashboard is created from the combined, cleaned data saved in `Data_Science_Jobs_Israel.csv`. It is a single, self-contained HTML file (`jobs_dashboard.html`) built using:

- **Plotly.js** for interactive charts and graphs  
- **Bootstrap 5** for responsive styling and UI components  

Key features visualized include:

- Time series of job counts per scraping run  
- Top hiring companies  
- Distribution of job posting sources  
- Most frequent keywords in job titles  
- Latest job postings with expandable details  
- A sortable, searchable table of all job listings  

The dashboard provides an accessible and regularly updated snapshot of the data science job market in Israel. It is hosted on GitHub Pages, accessible via the URL above.

---

## Usage

- Run `python scraper.py` to scrape new jobs and update the CSV file locally.  
- The GitHub Actions workflow automates this on the main branch every 12 hours.  
- View the updated interactive dashboard online at the GitHub Pages URL.

---

## Requirements

- Python 3.11.8
- Packages: `requests`, `beautifulsoup4`, `pandas`, `fake-useragent`, `plotly` (for local HTML generation)  

Install dependencies via:

```bash
pip install -r requirements.txt
