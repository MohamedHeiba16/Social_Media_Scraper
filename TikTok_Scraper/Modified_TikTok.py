import logging
import json
import time
import re
import random
import math
from datetime import datetime
from typing import List, Dict, Any

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from fake_useragent import UserAgent
from cachetools import TTLCache

# Import Captcha Solver
from tiktok_captcha_solver import SeleniumSolver

class AdvancedTikTokScraper:
    def __init__(self, config_path='config.json', captcha_api_key=None):
        self.config = self.load_config(config_path)
        self.driver = None
        self.ua = UserAgent()
        self.cache = TTLCache(maxsize=100, ttl=3600)
        self.logger = self.setup_logger()
        
        # Captcha Solver Configuration
        self.captcha_api_key = captcha_api_key or self.config.get('captcha_api_key')
        self.captcha_solver = None

    def setup_logger(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            raise
    
    def setup_driver(self):
        # Undetected ChromeDriver Configuration
        chrome_options = uc.ChromeOptions()
        
        # Randomized Browser Configuration
        viewport_width = random.randint(1024, 1920)
        viewport_height = random.randint(768, 1080)
        
        user_agent = self.ua.random
        platform = random.choice(['Windows', 'Macintosh'])
        language = random.choice(['en-US', 'en-GB', 'en-CA'])
        
        # Anti-Detection Options
        chrome_options.add_argument(f'--window-size={viewport_width},{viewport_height}')
        chrome_options.add_argument(f'user-agent={user_agent}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        
        # Language and Platform Headers
        chrome_options.add_argument(f'--lang={language}')
        
        # Headless mode configuration
        if self.config.get('headless', False):
            chrome_options.add_argument('--headless=new')

        # Use undetected_chromedriver
        driver = uc.Chrome(options=chrome_options)

        # Customize additional browser properties
        driver.execute_cdp_cmd('Emulation.setUserAgentOverride', {
            "platform": platform,
            "userAgent": user_agent
        })

        return driver

    def solve_captcha_if_present(self, context='general'):
        if not self.captcha_api_key:
            self.logger.warning("No CAPTCHA API key provided. Manual solving required.")
            return False

        try:
            if not self.captcha_solver:
                self.captcha_solver = SeleniumSolver(
                    self.driver, 
                    self.captcha_api_key, 
                    mouse_step_size=2,  
                    mouse_step_delay_ms=25  
                )

            captcha_locators = [
                (By.XPATH, "//div[contains(@class, 'captcha')]"),
                (By.XPATH, "//div[contains(@id, 'captcha')]"),
                (By.XPATH, "//iframe[contains(@title, 'captcha')]")
            ]

            for locator in captcha_locators:
                try:
                    captcha_element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(locator)
                    )
                    
                    self.logger.info(f"CAPTCHA detected in {context} context. Attempting to solve...")
                    
                    solve_result = self.captcha_solver.solve_captcha_if_present()
                    
                    if solve_result:
                        # Explicitly check for different response types
                        if solve_result.angle is not None or solve_result.slide_x_proportion is not None:
                            self.logger.info(f"CAPTCHA successfully solved in {context} context.")
                            time.sleep(random.uniform(2, 5))
                            return True
                        else:
                            self.logger.warning(f"Invalid CAPTCHA solution for {context}")
                            return False
                    else:
                        self.logger.warning(f"CAPTCHA solving failed in {context} context.")
                        return False

                except TimeoutException:
                    continue

            return False

        except Exception as e:
            self.logger.error(f"Comprehensive CAPTCHA solving error for {context}: {e}")
            return False

    def login(self):
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                self.driver.get(self.config['login']['url'])
                
                # Wait for login page to load
                time.sleep(random.uniform(2, 5))
                
                # Solve CAPTCHA if present
                self.solve_captcha_if_present(context='login')
                
                # Locate and fill email field
                email_field = self.wait_and_find_element(By.CSS_SELECTOR, "input[type='text']")
                if email_field:
                    self.simulate_human_typing(email_field, self.config['login']['email'])
                    time.sleep(random.uniform(0.5, 1.5))
                else:
                    self.logger.error("Email field not found")
                    continue

                # Locate and fill password field
                password_field = self.wait_and_find_element(By.CSS_SELECTOR, "input[type='password']")
                if password_field:
                    self.simulate_human_typing(password_field, self.config['login']['password'])
                    time.sleep(random.uniform(1, 2))
                else:
                    self.logger.error("Password field not found")
                    continue

                # Locate and click login button
                login_button = self.wait_and_find_element(By.CSS_SELECTOR, "button[type='submit']")
                if login_button:
                    self.random_mouse_move(self.driver)
                    time.sleep(random.uniform(0.5, 1))
                    login_button.click()
                    
                    # Additional CAPTCHA solving after login attempt
                    solve_result = self.solve_captcha_if_present(context='post-login')
                    
                    # Check login success
                    time.sleep(random.uniform(2, 5))
                    if "login" not in self.driver.current_url.lower():
                        self.logger.info("Login successful!")
                        return
                    else:
                        self.logger.warning(f"Login attempt {attempt + 1} failed")
                        continue

                else:
                    self.logger.error("Login button not found")
                    continue

            except Exception as e:
                self.logger.error(f"Login attempt {attempt + 1} failed: {e}")
                time.sleep(random.uniform(2, 5))  # Wait between attempts
                continue

        # If all attempts fail
        raise Exception("Login failed after maximum attempts. Please check credentials and CAPTCHA handling.")

    def scrape_profile(self, username):
        try:
            profile_url = f"https://www.tiktok.com/@{username}"
            self.logger.info(f"Scraping profile: {profile_url}")
            
            # Navigate to profile
            self.driver.get(profile_url)
            
            # Solve CAPTCHA if present
            self.solve_captcha_if_present(context='profile')
            
            # Wait for page to load
            time.sleep(random.uniform(2, 5))

            # Get all video links
            post_links = []
            try:
                posts = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, '//div[@class=" css-13fa1gi-DivWrapper e1cg0wnj1"]/a'))
                )
                
                for post in posts:
                    link = post.get_attribute('href')
                    if '/video/' in link:
                        post_links.append(link)
            except Exception as e:
                self.logger.warning(f"Error finding post links for {username}: {e}")
                return []

            posts_data = []
            for video_link in post_links[:5]:  # Limit to first 5 posts
                try:
                    # Navigate to video
                    self.driver.get(video_link)
                    
                    # Solve CAPTCHA if present for individual video
                    self.solve_captcha_if_present(context='video')
                    
                    time.sleep(random.uniform(1, 3))

                    # Get timestamp from video ID
                    timestamp = self.get_timestamp_from_video_id(video_link)

                    # Extract metrics
                    meta_desc = self.wait_and_find_element(By.XPATH, '//meta[@name="description"]')
                    if not meta_desc:
                        continue

                    description = meta_desc.get_attribute('content')
                    metrics = self.extract_metrics_from_meta(description)

                    post_data = {
                        "username": username,
                        "timestamp": timestamp,
                        "content": metrics['content'],
                        "likes": metrics['likes'],
                        "comments": metrics['comments'],
                        "shares": metrics['shares'],
                        "url": video_link
                    }
                    posts_data.append(post_data)

                except Exception as e:
                    self.logger.warning(f"Error scraping video {video_link}: {e}")
                    continue

            return posts_data

        except Exception as e:
            self.logger.error(f"Error scraping profile {username}: {e}")
            return []

    def simulate_human_typing(self, element, text):
        """Simulate human-like typing with random speeds and occasional typos"""
        for char in text:
            element.send_keys(char)
            # Random typing speed
            time.sleep(random.uniform(0.05, 0.2))
            
            # Occasional typo simulation
            if random.random() < 0.02:  # 2% chance of typo
                wrong_char = random.choice('qwertyuiop')
                element.send_keys(wrong_char)
                time.sleep(0.3)
                element.send_keys(Keys.BACKSPACE)

    def random_mouse_move(self, driver):
        """Simulate random mouse movements"""
        actions = ActionChains(driver)
        width = driver.execute_script("return window.innerWidth")
        height = driver.execute_script("return window.innerHeight")

        xoffset = random.randint(0, width - 1)  # Ensure within bounds
        yoffset = random.randint(0, height - 1)

        try:
            actions.move_by_offset(xoffset, yoffset).perform()
        except Exception as e:
            self.logger.warning(f"Random mouse move failed: {e}")
    def get_timestamp_from_video_id(self, video_link):
        # Rest of the method remains the same as in the original script
        match = re.search(r'/video/(\d+)', video_link)
        if not match:
            return None
        
        video_id = int(match.group(1))
        binary_representation = bin(video_id)[2:]
        binary_31_bits = binary_representation[:31]
        decimal_value = int(binary_31_bits, 2)
        timestamp = datetime.utcfromtimestamp(decimal_value)
        return timestamp.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    def convert_value(self, value_str):
        if not value_str:
            return 0
        
        value_str = value_str.strip().replace(',', '')
        
        try:
            if 'K' in value_str:
                return int(float(value_str.replace('K', '')) * 1000)
            elif 'M' in value_str:
                return int(float(value_str.replace('M', '')) * 1000000)
            return int(value_str)
        except (ValueError, TypeError):
            return 0

    def extract_metrics_from_meta(self, description):
        # Cache key based on description hash
        cache_key = f"metrics_{hash(description)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        metrics = {
            'likes': 0,
            'comments': 0,
            'shares': 0,
            'content': ""
        }

        try:
            # Extract likes
            likes_element = self.wait_and_find_element(
                By.XPATH, "//strong[@data-e2e='like-count']"
            )
            if likes_element:
                metrics['likes'] = self.convert_value(likes_element.text)

            # Extract comments
            comments_element = self.wait_and_find_element(
                By.XPATH, "//strong[@data-e2e='comment-count']"
            )
            if comments_element:
                metrics['comments'] = self.convert_value(comments_element.text)

            # Extract shares
            shares_element = self.wait_and_find_element(
                By.XPATH, "//strong[@data-e2e='share-count']"
            )
            if shares_element:
                metrics['shares'] = self.convert_value(shares_element.text)

            # Extract content
            content_element = self.wait_and_find_element(
                By.XPATH, "//h1[@data-e2e='browse-video-desc']/span"
            )
            if content_element:
                metrics['content'] = content_element.text.strip()

            # Cache the results
            self.cache[cache_key] = metrics
            return metrics

        except Exception as e:
            self.logger.error(f"Error extracting metrics: {str(e)}")
            return metrics

    def wait_and_find_element(self, by, value, timeout=10):
        """Helper method to wait and find an element"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            self.logger.warning(f"Element not found: {by}={value}")
            return None 

    def run(self):
        max_retry_attempts = 3
        retry_count = 0

        while retry_count < max_retry_attempts:
            try:
                self.driver = self.setup_driver()
                self.login()
                
                all_data = {"TikTok": []}
                for username in self.config['target_profiles']:
                    try:
                        time.sleep(random.uniform(2, 5))  # Random delay between profile scrapes
                        posts = self.scrape_profile(username)
                        all_data["TikTok"].extend(posts)
                    except Exception as profile_error:
                        self.logger.warning(f"Error scraping profile {username}: {profile_error}")
                        continue

                with open(self.config['output_file'], 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, indent=2, ensure_ascii=False)

                break  # Successful run, exit the retry loop

            except Exception as e:
                self.logger.error(f"Scraping attempt {retry_count + 1} failed: {e}")
                retry_count += 1
                if self.driver:
                    self.driver.quit()

            finally:
                if self.driver:
                    try:
                        self.driver.quit()
                    except Exception:
                        pass

        if retry_count == max_retry_attempts:
            self.logger.error("Failed to complete scraping after multiple attempts.")

if __name__ == "__main__":
    # Make sure to replace 'YOUR_CAPTCHA_API_KEY' with your actual API key
    scraper = AdvancedTikTokScraper(captcha_api_key='5383164b93f50df203eeb761e2f39794')
    scraper.run()