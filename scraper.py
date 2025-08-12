import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
from fake_useragent import UserAgent
import pandas as pd
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import re


class JobScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        self.session.headers = self._get_headers()
        self.run_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    def _get_headers(self):
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
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
    
    def extract_linkedin_job_id(self, url):
        """Extract LinkedIn job ID from URL using regex"""
        match = re.search(r'-(\d+)(?:\?|$)', url)
        return match.group(1) if match else None

    def _parse_linkedin_page(self, soup):
        """Parse LinkedIn job cards from page source"""
        # Try multiple selectors as LinkedIn changes their classes frequently
        job_cards = soup.find_all('li', class_='jobs-search-results__list-item') or \
                    soup.find_all('div', class_='base-card') or \
                    soup.find_all('div', class_='job-card-container')
        
        jobs = []
        for card in job_cards:
            try:
                # Extract job link and ID
                link_elem = card.find('a', class_='base-card__full-link') or \
                            card.find('a', class_='job-card-container__link')
                link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else None
                job_id = self.extract_linkedin_job_id(link) if link else None
                
                # Extract job title
                title_elem = card.find('h3', class_='base-search-card__title') or \
                             card.find('h3', class_='job-card-list__title')
                title = title_elem.text.strip() if title_elem else None
                
                # Extract company
                company_elem = card.find('h4', class_='base-search-card__subtitle') or \
                               card.find('a', class_='job-card-container__company-name')
                company = company_elem.text.strip() if company_elem else None
                
                # Extract location
                location_elem = card.find('span', class_='job-search-card__location') or \
                                card.find('li', class_='job-card-container__metadata-item')
                location = location_elem.text.strip() if location_elem else None
                
                jobs.append({
                    "title": title,
                        "company": company,
                        "location": location,
                        "link": link,
                        "source": "LinkedIn",
                        "job_id": job_id,
                        "run_time": self.run_time
                })
                
            except Exception as e:
                print(f"Error parsing job card: {e}")
                continue
        
        print(f"Found {len(job_cards)} job cards, parsed {len(jobs)} jobs")
        return jobs, len(jobs)

    def _scrape_linkedin(self, position, country, max_results):
        """Scrape LinkedIn job listings"""
        all_jobs = []
        unique_job_ids = set()
        
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'user-agent={self.ua.random}')
        
        # Initialize WebDriver
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        try:
            # Build URL
            base_url = "https://www.linkedin.com/jobs/search"
            params = {
                'keywords': position,
                'location': country,
                'geoId': '101620260',  # Israel
                'f_TPR': 'r86400'  # Last 24 hours
            }
            query_string = '&'.join(f"{k}={v}" for k, v in params.items())
            url = f"{base_url}?{query_string}"
            
            driver.get(url)
            print(f"Opened LinkedIn: {url}")
            
            # Wait for initial jobs to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search__results-list"))
            )
            time.sleep(3)  # Additional wait for content
            
            # Initialize scroll variables
            last_height = driver.execute_script("return document.body.scrollHeight")
            consecutive_no_new_jobs = 0
            job_count = 0
            scroll_attempts = 0
            MAX_SCROLL_ATTEMPTS = 20
            
            while job_count < max_results and scroll_attempts < MAX_SCROLL_ATTEMPTS:
                scroll_attempts += 1
                
                # Scroll to bottom with JavaScript
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Random wait for content to load
                time.sleep(random.uniform(1.5, 3.0))
                
                # Try clicking "See more jobs" button if available
                try:
                    see_more_button = driver.find_element(
                        By.XPATH, "//button[contains(@aria-label, 'See more jobs')]"
                    )
                    if see_more_button.is_displayed():
                        ActionChains(driver).move_to_element(see_more_button).click().perform()
                        print("Clicked 'See more jobs' button")
                        time.sleep(2)
                except (NoSuchElementException, ElementNotInteractableException):
                    pass
                
                # Check if new content loaded
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print("No height change detected")
                    consecutive_no_new_jobs += 1
                else:
                    consecutive_no_new_jobs = 0
                last_height = new_height
                
                # Parse current page
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                jobs, count = self._parse_linkedin_page(soup)
                
                # Process new jobs
                new_jobs = []
                for job in jobs:
                    job_id = job.get('job_id')
                    if job_id and job_id not in unique_job_ids:
                        unique_job_ids.add(job_id)
                        new_jobs.append(job)
                
                job_count += len(new_jobs)
                all_jobs.extend(new_jobs)
                print(f"Added {len(new_jobs)} new jobs (Total: {job_count})")
                
                # Exit conditions
                if consecutive_no_new_jobs >= 3:
                    print("No new jobs detected after multiple scrolls")
                    break
                if job_count >= max_results:
                    print(f"Reached max results ({max_results})")
                    break
            
            # Save final page source for debugging
            with open('linkedin_final.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("Saved final page source to linkedin_final.html")
            
            return pd.DataFrame(all_jobs[:max_results])
        
        except Exception as e:
            print(f"Error during LinkedIn scraping: {str(e)}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
        finally:
            driver.quit()
    
      

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
    linkedin_df = scraper.scrape("linkedin.com", POSITION, COUNTRY, max_results=10000)
    linkedin_df = linkedin_df.drop_duplicates(subset=['link']).reset_index(drop=True)
    print("Scraping Google Careers for DS jobs...", flush=True)
    google_df = scraper.scrape("google.com", POSITION, COUNTRY)
    google_df = google_df.drop_duplicates(subset=['link']).reset_index(drop=True)

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
