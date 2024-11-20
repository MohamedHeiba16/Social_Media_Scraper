import time
import random
import json
import logging
import asyncio
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from fake_useragent import UserAgent
from datetime import datetime


class InstagramScraper:
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.driver = None
        self.session_start_time = None

    def _load_config(self, config_path):
        with open(config_path, "r") as f:
            return json.load(f)

    def _setup_logger(self):
        # Enhanced logging configuration
        logging.basicConfig(
            level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("instagram_scraper_debug.log"),
                logging.StreamHandler(),
            ],
        )
        return logging.getLogger("InstagramScraper")

    def _get_random_delay(self):
        base_delay = random.uniform(2, 4)  # Increased base delay
        # Add random micro-delays
        micro_delay = random.uniform(0.1, 0.5) * random.random()
        return base_delay + micro_delay

    def _setup_driver(self):
        options = webdriver.ChromeOptions()

        # Enhanced anti-detection measures
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")

        # Random viewport size
        viewport_width = random.randint(1024, 1920)
        viewport_height = random.randint(768, 1080)
        options.add_argument(f"--window-size={viewport_width},{viewport_height}")

        # Randomized user agent
        ua = UserAgent()
        user_agent = ua.random
        options.add_argument(f"user-agent={user_agent}")

        # Additional ChromeOptions
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # Add random language and platform
        languages = ["en-US", "en-GB", "en-CA", "en-AU"]
        platforms = [
            "Windows NT 10.0",
            "Macintosh; Intel Mac OS X 10_15_7",
            "X11; Linux x86_64",
        ]
        options.add_argument(f"--lang={random.choice(languages)}")
        options.add_argument(f"--platform={random.choice(platforms)}")

        self.driver = webdriver.Chrome(options=options)

        # Additional JavaScript-based evasion
        self._inject_evasion_scripts()
        self.session_start_time = datetime.now()

    def _inject_evasion_scripts(self):
        evasion_scripts = [
            # Mask webdriver presence
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
            
            # Add random plugins
            """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5].map(() => ({
                    name: Math.random().toString(36),
                    filename: Math.random().toString(36)
                }))
            })
            """,
            
            # Randomize hardware concurrency
            f"Object.defineProperty(navigator, 'hardwareConcurrency', {{get: () => {random.randint(2, 16)}}})",
            
            # Add random screen properties
            f"""
            Object.defineProperty(window, 'screen', {{
                get: () => ({{
                    width: {random.randint(1024, 1920)},
                    height: {random.randint(768, 1080)},
                    colorDepth: {random.choice([24, 32])},
                    pixelDepth: {random.choice([24, 32])}
                }})
            }})
            """
        ]

        for script in evasion_scripts:
            self.driver.execute_script(script)

    async def login(self):
        try:
            self._setup_driver()

            # Random pre-login behavior
            starter_urls = [
                "https://www.instagram.com/explore/",
                "https://www.instagram.com/about/us/",
                "https://help.instagram.com/",
            ]
            self.driver.get(random.choice(starter_urls))
            await asyncio.sleep(self._get_random_delay())

            self.driver.get("https://www.instagram.com/accounts/login/")
            await asyncio.sleep(self._get_random_delay())

            # Handle cookie consent with multiple possible selectors
            cookie_selectors = [
                "//button[contains(text(), 'Accept')]",
                "//button[contains(text(), 'Allow')]",
                "//button[contains(@class, 'consent')]",
            ]

            for selector in cookie_selectors:
                try:
                    cookie_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    cookie_button.click()
                    break
                except TimeoutException:
                    continue

            # Enhanced human-like typing
            username_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password_input = self.driver.find_element(By.NAME, "password")

            await self._human_like_type(
                username_input, self.config["credentials"]["Instagram"]["username"]
            )
            await asyncio.sleep(self._get_random_delay())
            await self._human_like_type(
                password_input, self.config["credentials"]["Instagram"]["password"]
            )

            # Random mouse movements before clicking login
            self._simulate_mouse_movement()

            login_button = self.driver.find_element(
                By.XPATH, "//button[@type='submit']"
            )
            login_button.click()

            # Handle various post-login popups
            popup_selectors = [
                "//button[contains(text(), 'Not Now')]",
                "//button[contains(text(), 'Skip')]",
                "//button[contains(text(), 'Maybe Later')]",
            ]

            await asyncio.sleep(self._get_random_delay() * 2)  # Longer wait after login

            for selector in popup_selectors:
                try:
                    popup_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    popup_button.click()
                    await asyncio.sleep(self._get_random_delay())
                except TimeoutException:
                    continue

            self.logger.info("Successfully logged in to Instagram")
            return True

        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            return False

    async def _human_like_type(self, element, text):
        for char in text:
            # Random typing speed
            typing_speed = random.uniform(0.1, 0.3)
            # Occasionally add a longer pause
            if random.random() < 0.1:
                typing_speed += random.uniform(0.1, 0.5)
            element.send_keys(char)
            await asyncio.sleep(typing_speed)

        # Occasionally make and correct "typos"
        if random.random() < 0.05:
            element.send_keys(random.choice(text))
            await asyncio.sleep(0.5)
            element.send_keys("")
            await asyncio.sleep(0.3)

    def _simulate_mouse_movement(self):
        try:
            from selenium.webdriver.common.action_chains import ActionChains

            actions = ActionChains(self.driver)

            # Generate random points for mouse movement
            points = [
                (random.randint(0, 1000), random.randint(0, 1000)) for _ in range(5)
            ]

            for x, y in points:
                actions.move_by_offset(x, y)
                actions.pause(random.uniform(0.1, 0.3))

            actions.perform()
        except Exception as e:
            self.logger.warning(f"Mouse movement simulation failed: {str(e)}")

    def _randomize_scroll(self):
        scroll_amount = random.randint(300, 700)
        scroll_time = random.uniform(1, 3)
        scroll_steps = random.randint(5, 10)

        for _ in range(scroll_steps):
            step = scroll_amount / scroll_steps
            self.driver.execute_script(f"window.scrollBy(0, {step})")
            time.sleep(scroll_time / scroll_steps)

    async def scrape_profile(self, username):
        try:
            self.logger.debug(f"Starting to scrape profile: {username}")

            # Log current URL before navigation
            self.logger.debug(f"Current URL: {self.driver.current_url}")

            self.driver.get(f"https://www.instagram.com/{username}/")
            await asyncio.sleep(self._get_random_delay() * 1.5)

            # Log page source for debugging
            self.logger.debug(f"Page title after navigation: {self.driver.title}")

            # Check if logged in
            if "Login" in self.driver.title:
                self.logger.error("Not logged in or session expired")
                return []

            # Try multiple selector variations for posts
            post_selectors = [
                "//a[contains(@href, '/p/')]",
                "//article//a[contains(@href, '/p/')]",
                "//div[contains(@class, 'v1Nh3')]//a",
            ]

            post_links = []
            for selector in post_selectors:
                try:
                    self.logger.debug(f"Trying post selector: {selector}")
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        post_links = [link.get_attribute("href") for link in elements]
                        self.logger.debug(
                            f"Found {len(post_links)} posts with selector {selector}"
                        )
                        break
                except Exception as e:
                    self.logger.debug(f"Selector {selector} failed: {str(e)}")

            if not post_links:
                self.logger.error("No posts found on profile")
                return []

            posts_to_scrape = min(
                self.config["socialMediaPlatforms"]["Instagram"]["postsPerProfile"],
                random.randint(5, 15),
            )

            self.logger.debug(f"Attempting to scrape {posts_to_scrape} posts")

            posts_data = []
            for link in post_links[:posts_to_scrape]:
                self.logger.debug(f"Scraping post: {link}")
                post_data = await self._scrape_post(link, username)
                if post_data:
                    posts_data.append(post_data)
                await asyncio.sleep(self._get_random_delay() * 2)

            self.logger.info(
                f"Successfully scraped {len(posts_data)} posts for {username}"
            )
            return posts_data

        except Exception as e:
            self.logger.error(
                f"Error scraping profile {username}: {str(e)}", exc_info=True
            )
            return []

    async def _scroll_profile_with_random_behavior(self, target_posts):
        posts_loaded = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while posts_loaded < target_posts:
            # Random scroll behavior
            self._randomize_scroll()

            # Occasionally pause scrolling
            if random.random() < 0.2:
                await asyncio.sleep(random.uniform(1, 3))

            # Sometimes move mouse while scrolling
            if random.random() < 0.3:
                self._simulate_mouse_movement()

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                # Try a few more times with different scroll amounts
                for _ in range(3):
                    self._randomize_scroll()
                    await asyncio.sleep(self._get_random_delay())
                    new_height = self.driver.execute_script(
                        "return document.body.scrollHeight"
                    )
                    if new_height != last_height:
                        break
                else:
                    break

            last_height = new_height
            posts_loaded = len(
                self.driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
            )

    async def _scrape_post(self, post_url, username):
        try:
            self.logger.debug(f"Starting to scrape post: {post_url}")

            self.driver.get(post_url)
            await asyncio.sleep(self._get_random_delay())

            # Get meta description content first
            try:
                content_data = (
                    WebDriverWait(self.driver, 10)
                    .until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//meta[@name="description"]')
                        )
                    )
                    .get_attribute("content")
                )

                self.logger.debug(f"Found meta description: {content_data}")

                # Extract comments using regex patterns
                comments = 0
                comments_patterns = [
                    r"([\d,\.]+[KkMm]?)\s*[Cc]omments",  # Matches "1.5K comments", "2M comments"
                    r"([\d,]+)\s*[Cc]omments",  # Matches "1,234 comments"
                    r"([0-9]+)\s*[Cc]omments",  # Matches "123 comments"
                ]

                for pattern in comments_patterns:
                    comments_match = re.search(pattern, content_data)
                    if comments_match:
                        comments_str = comments_match.group(1).lower().replace(",", "")
                        # Handle K/M suffixes
                        if "k" in comments_str:
                            comments = int(float(comments_str.replace("k", "")) * 1000)
                        elif "m" in comments_str:
                            comments = int(
                                float(comments_str.replace("m", "")) * 1000000
                            )
                        else:
                            comments = int(float(comments_str))
                        break

                self.logger.debug(f"Extracted comments count: {comments}")
            except Exception as e:
                self.logger.debug(f"Meta description extraction failed: {str(e)}")

                # Fallback to traditional selectors if meta description fails
                comments_selectors = [
                    "//span[@class='_ae5q']",
                    "//div[contains(@class, '_ae2s')]//span",
                    "//span[contains(text(), 'comments')]",
                ]

                for selector in comments_selectors:
                    try:
                        element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        comments_text = element.text
                        comments_text = (
                            comments_text.lower()
                            .replace(",", "")
                            .replace("comments", "")
                            .replace("k", "000")
                            .strip()
                        )
                        comments = int(float(comments_text))
                        if comments > 0:
                            self.logger.debug(
                                f"Found comments using fallback selector: {selector}"
                            )
                            break
                    except Exception as selector_e:
                        self.logger.debug(
                            f"Comments selector {selector} failed: {str(selector_e)}"
                        )

            content_selectors = [
                "//div[contains(@class, '_a9zs')]//h1",
                "//div[contains(@class, '_a9zs')]//span",
                "//div[contains(@class, 'C4VMK')]//span",
            ]

            content = ""
            for selector in content_selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    content = element.text
                    if content:
                        break
                except Exception as e:
                    self.logger.debug(f"Content selector {selector} failed: {str(e)}")

            # Extract timestamp
            timestamp_selectors = [
                "//time[@datetime]",
                "//div[@class='_a9zr']//time",
                "//time[@class='_aaqe']",
            ]

            timestamp = ""
            for selector in timestamp_selectors:
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    timestamp = element.get_attribute("datetime")
                    if timestamp:
                        break
                except Exception as e:
                    self.logger.debug(f"Timestamp selector {selector} failed: {str(e)}")

            # Extract likes from meta description if available
            likes = 0
            try:
                likes_match = re.search(r"([\d,\.]+[KkMm]?)\s*[Ll]ikes", content_data)
                if likes_match:
                    likes_str = likes_match.group(1).lower().replace(",", "")
                    if "k" in likes_str:
                        likes = int(float(likes_str.replace("k", "")) * 1000)
                    elif "m" in likes_str:
                        likes = int(float(likes_str.replace("m", "")) * 1000000)
                    else:
                        likes = int(float(likes_str))
            except Exception as e:
                self.logger.debug(f"Likes extraction from meta failed: {str(e)}")
                likes = 0

            if likes == 0:
                self.logger.debug("Attempting fallback methods for likes extraction")

                # Method 1: Try the likes button with various selectors
                likes_button_selectors = [
                    "//button[contains(@class, '_abl-')]//span[contains(text(), 'like')]",
                    "//button[contains(@class, '_abl-')]//span",
                    "//section//div[contains(text(), 'likes')]",
                    "//a[contains(@href, 'liked_by')]//span",
                ]

                for selector in likes_button_selectors:
                    try:
                        likes_element = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        likes_text = likes_element.text.lower()
                        if likes_text:
                            # Remove non-numeric characters except '.' and 'k'/'m'
                            likes_text = "".join(
                                c for c in likes_text if c.isdigit() or c in ".,km"
                            )
                            if "k" in likes_text:
                                likes = int(float(likes_text.replace("k", "")) * 1000)
                            elif "m" in likes_text:
                                likes = int(
                                    float(likes_text.replace("m", "")) * 1000000
                                )
                            else:
                                likes = int(float(likes_text))
                            if likes > 0:
                                self.logger.debug(
                                    f"Found likes using button selector: {selector}"
                                )
                                break
                    except Exception as e:
                        self.logger.debug(
                            f"Likes button selector {selector} failed: {str(e)}"
                        )

            post_data = {
                "username": username,
                "timestamp": timestamp,
                "content": content,
                "likes": likes,
                "comments": comments,
                "url": post_url
            }

            self.logger.info(f"Successfully scraped post data: {post_data}")
            return post_data

        except Exception as e:
            self.logger.error(
                f"Error scraping post {post_url}: {str(e)}", exc_info=True
            )
            return None

    async def save_to_json(self, posts_data):
        try:
            output_file = (
                f"instagram_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(posts_data, f, ensure_ascii=False, indent=4)
            self.logger.info(f"Data saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Error saving data to JSON: {str(e)}")

    def cleanup(self):
        if self.driver:
            self.driver.quit()


async def main():
    scraper = InstagramScraper("config.json")
    all_posts_data = []

    try:
        if await scraper.login():
            # Randomize the order of accounts
            accounts = scraper.config["socialMediaPlatforms"]["Instagram"]["accounts"]
            random.shuffle(accounts)

            for username in accounts:
                scraper.logger.info(f"Scraping profile: {username}")
                posts = await scraper.scrape_profile(username)
                all_posts_data.extend(posts)
                # Random delay between profiles
                await asyncio.sleep(random.uniform(5, 10))

            await scraper.save_to_json(all_posts_data)
    finally:
        scraper.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
