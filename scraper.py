import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
from fake_useragent import UserAgent
import pandas as pd
import subprocess


class JobScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers = self._get_headers()
        self.run_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    def _get_headers(self):
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def scrape(self, website, position, country, max_results=None):
        website = website.lower().strip()
        if 'linkedin.com' in website:
            return self._scrape_linkedin(position, country, max_results)
        elif 'google.com' in website:
            return self._scrape_google(position, country)
        return pd.DataFrame()

    def _scrape_google(self, position, country):
        all_jobs = []
        base_url = "https://www.google.com/about/careers/applications/jobs/results/"
        params = {
            "q": f"'{position}'",
            "location": country
        }
        
        try:
            # Fetch job search page
            response = self.session.get(base_url, params=params, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all job cards
            job_cards = soup.find_all('li', class_='lLd3Je')
            
            for card in job_cards:
                try:
                    title = card.find('h3', class_='QJPWVe').text.strip()
                    company = "Google"
                    
                    # Extract location
                    location_div = card.find('div', class_='vbZS6e')
                    location = location_div.text.strip() if location_div else "Israel"
                    
                    # Extract job ID from link
                    link_tag = card.find('a', class_='WpHeLc')
                    if not link_tag:
                        continue
                    relative_link = link_tag.get('href')
                    job_id = relative_link.split('/')[-2] if relative_link else ""
                    link = f"https://www.google.com/about/careers/applications/{relative_link}"
                    
                    all_jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "link": link,
                        "source": "Google Careers",
                        "job_id": job_id,
                        "run_time": self.run_time
                    })
                except Exception as e:
                    print(f"Error parsing Google job card: {e}", flush=True)
                    continue
                    
            print(f"Google Careers: Found {len(all_jobs)} DS jobs", flush=True)
        except Exception as e:
            print(f"Google Careers error: {str(e)}", flush=True)
        return pd.DataFrame(all_jobs)

    def _scrape_linkedin(self, position, country, max_results):
        all_jobs = []
        base_url = "https://www.linkedin.com/jobs/search"
        max_retries = 3
        start = 0
        
        # LinkedIn parameters
        params = {
            'keywords': position,
            'location': country,
            'geoId': '101620260',
            'trk': 'public_jobs_jobs-search-bar_search-submit',
            'position': 1,
            'pageNum': 0,
            'f_TPR': 'r86400'
        }
        
        while start < max_results:
            params['start'] = start
            
            for attempt in range(max_retries):
                try:
                    response = self.session.get(base_url, params=params, timeout=15)
                    if response.status_code == 429:
                        wait = 60 + random.randint(0, 30)
                        print(f"Rate limited. Waiting {wait} seconds...", flush=True)
                        time.sleep(wait)
                        continue
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    jobs, total_results = self._parse_linkedin_page(soup)
                    self.jobs = jobs
                    self.tota_results = total_results
                    all_jobs.extend(jobs)
                    
                    if len(jobs) == 0:
                        print("No more jobs found", flush=True)
                        return pd.DataFrame(all_jobs)
                    
                    print(f"Page {start//25 + 1}: Added {len(jobs)} jobs (Total: {len(all_jobs)})", flush=True)
                    start += 25
                    time.sleep(random.uniform(2, 4))
                    break
                    
                except Exception as e:
                    print(f"Attempt {attempt+1} failed: {str(e)}", flush=True)
                    time.sleep(10)
            else:
                print("Max retries exceeded", flush=True)
                break
                
        return pd.DataFrame(all_jobs[:max_results])

    def _parse_linkedin_page(self, soup):
        jobs = []

        total_results = 0
        results_text = soup.find('span', class_='results-context-header__job-count')
        if results_text:
            try:
                total_results = int(results_text.text.replace(',', ''))
            except:
                pass
        
        # Find job cards
        job_cards = soup.find_all('div', class_='base-card')
        
        for card in job_cards:
            try:
                job_id = card.get('data-entity-urn', '').split(':')[-1]
                title = card.find('h3', class_='base-search-card__title').text.strip()
                company = card.find('h4', class_='base-search-card__subtitle').text.strip()
                location = card.find('span', class_='job-search-card__location').text.strip()
                link = card.find('a', class_='base-card__full-link')['href'].split('?')[0]
                
                jobs.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'link': link,
                    'source': 'LinkedIn',
                    'job_id': job_id,
                    "run_time": self.run_time
                })
            except Exception as e:
                continue
        return jobs, total_results

def launch_dashboard():
    """Launch the Streamlit dashboard in a separate process"""
    print("\nLaunching dashboard...", flush=True)
    print("Dashboard will open in your default browser automatically", flush=True)
    print("Press Ctrl+C in this terminal to stop both the dashboard and scraper", flush=True)
    
    try:
        # Run the dashboard in a subprocess
        dashboard_process = subprocess.Popen(
            ["streamlit", "run", "dashboard.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Stream the output so we can see it
        for line in iter(dashboard_process.stdout.readline, ''):
            print(line, end='', flush=True)
        
        dashboard_process.wait()
    except FileNotFoundError:
        print("Error: Streamlit not found. Please install with: pip install streamlit", flush=True)
    except Exception as e:
        print(f"Failed to launch dashboard: {e}", flush=True)

if __name__ == "__main__":

    # Configuration
    COUNTRY = "Israel"
    POSITION = "Data Scientist"
    CSV_FILE = f"Data_Science_Jobs_{COUNTRY}.csv"
    
    # Initialize scraper
    scraper = JobScraper()
    
    # Scrape sources
    print("Scraping LinkedIn for DS jobs...", flush=True)
    linkedin_df = scraper.scrape("linkedin.com", POSITION, COUNTRY, max_results=100)
    print("Scraping Google Careers for DS jobs...", flush=True)
    google_df = scraper.scrape("google.com", POSITION, COUNTRY)
    
    # Combine results
    all_jobs = pd.concat([linkedin_df, google_df], ignore_index=True)
    
    # Save/update CSV
    if os.path.exists(CSV_FILE):
        existing = pd.read_csv(CSV_FILE)
        updated = pd.concat([existing, all_jobs])
        updated.to_csv(CSV_FILE, index=False)
        print(f"Updated CSV. Total DS jobs: {len(updated)}", flush=True)
    else:
        all_jobs.to_csv(CSV_FILE, index=False)
        print(f"Created new CSV with {len(all_jobs)} DS jobs", flush=True)
