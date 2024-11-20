"""
Twitter Scraper - A stealth web scraping tool for Twitter/X
Uses advanced anti-detection measures and human-like behavior patterns.
Version: 1.0
"""

import atexit
import json
import logging
import psutil
import random
import re
import signal
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc


class TwitterScraper:
    """
    A sophisticated Twitter scraper that mimics human behavior and bypasses detection.
    
    Features:
    - Stealth browsing using undetected_chromedriver
    - Human-like scrolling and typing patterns
    - Advanced anti-detection measures
    - Automatic cleanup of browser processes
    """

    def __init__(self, config_path: str = 'config.json'):
        """
        Initialize the scraper with configuration settings.
        
        Args:
            config_path: Path to the configuration JSON file
        """
        self.config = self._load_config(config_path)
        self._setup_logging()
        self.driver: Optional[uc.Chrome] = None
        self.session_cookies: Optional[List[Dict]] = None
        self.last_action_time: float = time.time()
        self.action_count: int = 0
        self._chrome_pid: Optional[int] = None
        atexit.register(self.force_cleanup)

    # region Configuration and Setup
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file."""
        with open(config_path, 'r') as f:
            return json.load(f)

    def _setup_logging(self) -> None:
        """Configure logging based on settings in config file."""
        logging.basicConfig(
            level=getattr(logging, self.config['logging']['level']),
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=self.config['logging']['logFilePath'] if self.config['logging']['logToFile'] else None
        )
        self.logger = logging.getLogger('StealthScraper')

    def _create_stealth_driver(self) -> uc.Chrome:
        """Create an undetectable Chrome instance with anti-detection measures."""
        options = self._configure_chrome_options()
        
        try:
            # Modify undetected_chromedriver's cleanup behavior
            uc.Chrome.__del__ = lambda self: self.quit() if hasattr(self, 'quit') else None
            
            driver = uc.Chrome(options=options)
            self._chrome_pid = driver.service.process.pid
            self._inject_stealth_js(driver)
            return driver
        except Exception as e:
            self.logger.error(f"Failed to create driver: {str(e)}")
            raise

    def _configure_chrome_options(self) -> uc.ChromeOptions:
        """Configure Chrome options for stealth operation."""
        options = uc.ChromeOptions()
        
        # Anti-detection arguments
        stealth_args = [
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--disable-infobars',
            '--disable-browser-side-navigation',
            '--disable-gpu',
            '--no-sandbox',
            '--no-first-run',
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-breakpad',
            '--disable-component-extensions-with-background-pages',
            '--disable-extensions',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--disable-renderer-backgrounding',
        ]
        
        for arg in stealth_args:
            options.add_argument(arg)

        # Random window size
        width = random.randint(1050, 1200)
        height = random.randint(800, 1000)
        options.add_argument(f'--window-size={width},{height}')
        
        # Random user agent
        ua = UserAgent()
        options.add_argument(f'user-agent={ua.chrome}')
        
        return options
    # endregion

    # region Anti-Detection Methods
    def _inject_stealth_js(self, driver: uc.Chrome) -> None:
        """Inject JavaScript to mask automation indicators."""
        stealth_js = """
        // Mask webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Handle permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
            Promise.resolve({state: Notification.permission}) :
            originalQuery(parameters)
        );
        
        // Randomize canvas fingerprint
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type) {
            const context = originalGetContext.apply(this, arguments);
            if (type === '2d') {
                const originalFillText = context.fillText;
                context.fillText = function() {
                    arguments[0] = arguments[0] + ' ';
                    return originalFillText.apply(this, arguments);
                }
            }
            return context;
        };
        
        // Add fake plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                { name: 'Chrome PDF Plugin', suffixes: 'pdf', description: 'Portable Document Format' },
                { name: 'Chrome PDF Viewer', suffixes: 'pdf', description: '' },
                { name: 'Native Client', suffixes: '', description: '' }
            ]
        });
        """
        driver.execute_script(stealth_js)

    def _human_like_delay(self) -> None:
        """Implement human-like delays between actions."""
        current_time = time.time()
        time_since_last = current_time - self.last_action_time
        
        base_delay = random.uniform(3, 5) if self.action_count > 10 else random.uniform(1, 2)
        delay = base_delay * (1 + random.uniform(-0.2, 0.2))
        
        if time_since_last < 0.5:
            delay += random.uniform(1, 2)
            
        time.sleep(delay)
        self.last_action_time = time.time()
        self.action_count = 0 if self.action_count > 10 else self.action_count + 1

    def _natural_scroll(self, scroll_distance: int) -> None:
        """Perform natural-looking scroll with variable speed."""
        start_pos = self.driver.execute_script("return window.pageYOffset;")
        current_pos = start_pos
        target_pos = start_pos + scroll_distance
        
        def easeInOutQuad(t: float) -> float:
            return t * t if t < 0.5 else -1 + (4 - 2 * t) * t
        
        steps = random.randint(20, 30)
        for i in range(steps + 1):
            t = i / steps
            next_pos = start_pos + (scroll_distance * easeInOutQuad(t))
            self.driver.execute_script(f"window.scrollTo(0, {next_pos});")
            time.sleep(random.uniform(0.01, 0.03))

    def _simulate_human_typing(self, element: webdriver.remote.webelement.WebElement, text: str) -> None:
        """Simulate human-like typing patterns."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))
            if random.random() < 0.1:
                time.sleep(random.uniform(0.3, 0.7))
    # endregion

    # region Core Functionality
    def login(self) -> None:
        """Perform login with human-like behavior."""
        try:
            credentials = self.config["credentials"]["X"]
            if not self.driver:
                self.driver = self._create_stealth_driver()

            self.driver.get('https://twitter.com/login')
            self._human_like_delay()

            # Handle username
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            self._simulate_human_typing(username_input, credentials["username"])
            self._click_next_button()

            # Handle email verification if needed
            try:
                self._handle_email_verification(credentials["e_mail"])
            except TimeoutException:
                self.logger.info("Email verification not required")

            # Handle password
            self._handle_password_entry(credentials["password"])
            
            self.session_cookies = self.driver.get_cookies()
            self.logger.info("Successfully logged in")

        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            raise

    def scrape_profile(self, handle: str) -> List[Dict]:
        """
        Scrape tweets from a profile with natural behavior.
        
        Args:
            handle: Twitter handle to scrape
            
        Returns:
            List of dictionaries containing tweet data
        """
        tweets = []
        try:
            self.driver.get(f'https://twitter.com/{handle}')
            self._human_like_delay()
            
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_attempts = 0
            
            while len(tweets) < self.config['scrapeSettings'].get('maxTweetsPerProfile', 20):
                self._natural_scroll(random.randint(300, 500))
                
                new_tweets = self._extract_tweets_from_page(handle)
                tweets.extend(tweet for tweet in new_tweets if tweet not in tweets)
                
                if not self._should_continue_scrolling(last_height, scroll_attempts):
                    break
                    
                self._human_like_delay()
            
            return tweets
            
        except Exception as e:
            self.logger.error(f"Failed to scrape profile {handle}: {str(e)}")
            return []

    def save_results(self, results: List[Dict]) -> None:
        """Save scraped data to JSON file."""
        output = {"X": results}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"twitter_scrape_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
            
        self.logger.info(f"Results saved to {filename}")
    # endregion

    # region Helper Methods
    def _click_next_button(self) -> None:
        """Click the 'Next' button with natural mouse movement."""
        next_button = self.driver.find_element(By.XPATH, "//span[text()='Next']")
        ActionChains(self.driver)\
            .move_to_element(next_button)\
            .pause(random.uniform(0.1, 0.3))\
            .click()\
            .perform()
        self._human_like_delay()

    def _handle_email_verification(self, email: str) -> None:
        """Handle email verification step if present."""
        mail_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        self._simulate_human_typing(mail_input, email)
        self._click_next_button()

    def _handle_password_entry(self, password: str) -> None:
        """Handle password entry step."""
        password_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        self._simulate_human_typing(password_input, password)
        
        login_button = self.driver.find_element(By.XPATH, "//span[text()='Log in']")
        ActionChains(self.driver)\
            .move_to_element(login_button)\
            .pause(random.uniform(0.2, 0.4))\
            .click()\
            .perform()

    def _extract_tweets_from_page(self, handle: str) -> List[Dict]:
        """Extract tweets from the current page."""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        tweets = []
        
        for tweet in soup.find_all('article'):
            try:
                tweet_data = {
                    "username": handle,
                    "timestamp": self._extract_timestamp(tweet),
                    "content": self._extract_content(tweet),
                    "likes": self._extract_metric(tweet, 'like'),
                    "retweets": self._extract_metric(tweet, 'retweet'),
                    "comments": self._extract_metric(tweet, 'reply')
                }
                tweets.append(tweet_data)
            except Exception as e:
                self.logger.warning(f"Failed to parse tweet: {str(e)}")
        
        return tweets

    def _should_continue_scrolling(self, last_height: int, scroll_attempts: int) -> bool:
        """Determine if scrolling should continue."""
        new_height = self.driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
            return scroll_attempts < 3
        return True

    def _extract_timestamp(self, tweet_element: BeautifulSoup) -> Optional[str]:
        """Extract timestamp from tweet element."""
        time_element = tweet_element.find('time')
        return time_element['datetime'] if time_element and 'datetime' in time_element.attrs else None

    def _extract_content(self, tweet_element: BeautifulSoup) -> str:
        """Extract content from tweet element."""
        content_element = tweet_element.find('div', {'data-testid': 'tweetText'})
        return content_element.text if content_element else ''

    def _extract_metric(self, tweet_element: BeautifulSoup, metric_type: str) -> int:
        """Extract metric (likes, retweets, replies) from tweet element."""
        metric_element = tweet_element.find('button', {'data-testid': metric_type})
        if metric_element and (aria_label := metric_element.get('aria-label')):
            try:
                return int(re.search(r'\d+', aria_label).group())
            except (ValueError, AttributeError):
                return 0
        return 0
    # endregion

# region Cleanup Methods
    def _kill_process_tree(self, pid: int) -> None:
        """Kill a process and all its children."""
        try:
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                try:
                    child.kill()
                except psutil.NoSuchProcess:
                    pass
            
            try:
                parent.kill()
            except psutil.NoSuchProcess:
                pass
            
        except psutil.NoSuchProcess:
            pass

    def force_cleanup(self) -> None:
        """Force cleanup of all related processes."""
        try:
            # Regular cleanup attempt
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    self.logger.warning("Failed to quit driver gracefully")
                
            # Kill Chrome process tree
            if self._chrome_pid:
                self._kill_process_tree(self._chrome_pid)
            
            # Clean up remaining automation-related chrome processes
            self._cleanup_remaining_processes()
                    
        except Exception as e:
            self.logger.error(f"Error during force cleanup: {str(e)}")
        finally:
            self.driver = None
            self._chrome_pid = None

    def _cleanup_remaining_processes(self) -> None:
        """Clean up any remaining chrome processes related to automation."""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'chrome' in proc.info['name'].lower():
                    cmdline = proc.cmdline()
                    if any('--disable-blink-features=AutomationControlled' in arg for arg in cmdline):
                        self._kill_process_tree(proc.pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def cleanup(self) -> None:
        """Clean up resources."""
        self.force_cleanup()

    def create_signal_handler(self):
        """Create a signal handler for graceful shutdown."""
        def signal_handler(signum, frame):
            if self:
                self.cleanup()
            sys.exit(1)
        return signal_handler
    # endregion


def main():
    """Main execution function."""
    scraper = None
    try:
        # Initialize scraper
        scraper = TwitterScraper()
        
        # Set up signal handler
        signal_handler = scraper.create_signal_handler()
        signal.signal(signal.SIGINT, signal_handler)
        
        # Login and scrape
        scraper.login()
        
        all_tweets = []
        for handle in scraper.config['socialMediaPlatforms']['X']['accounts']:
            tweets = scraper.scrape_profile(handle)
            all_tweets.extend(tweets)
            time.sleep(random.uniform(30, 60))  # Pause between profiles
        
        scraper.save_results(all_tweets)
        
    except Exception as e:
        logging.error(f"Scraping failed: {str(e)}")
    finally:
        if scraper:
            scraper.cleanup()


if __name__ == "__main__":
    main()