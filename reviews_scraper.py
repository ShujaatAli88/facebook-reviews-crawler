from constants import FacebookContants, LoginCredentials, FacebookDataTable
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep
import pickle
import os
from model import Review
from uuid import uuid4
from database_handler import PostgresDBHandler


class ReviewsScraper:
    """
    A class to scrape reviews from Facebook pages based on location and category.
    This class handles the setup of the Selenium WebDriver, login to Facebook,
    searching for pages, and extracting review details.
    """
    def __init__(self):
        self.driver = None
        self.page_category = None
        self.page_location = None
        self.detail_pages = []

    def setup_driver(self):
        """
        Sets up the Chrome WebDriver with necessary options and configurations.
        This method initializes the WebDriver and configures it to avoid detection
        as an automated browser.
        """
        print("Setting up the Chrome driver...")
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        )
        self.driver = webdriver.Chrome(options=options)

    def load_cookies(self):
        """
        Loads cookies from a file to maintain the logged-in session.
        This method checks if a cookies file exists and attempts to load it.
        If successful, it refreshes the page to apply the cookies.
        """
        if os.path.exists("fb_cookies.pkl"):
            print("Cookies file found. Trying to load cookies...")
            self.driver.get("https://www.facebook.com")
            with open("fb_cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    if "sameSite" in cookie and cookie["sameSite"] not in [
                        "Lax",
                        "Strict",
                        "None",
                    ]:
                        cookie.pop("sameSite")
                    if "expiry" in cookie and isinstance(cookie["expiry"], float):
                        cookie["expiry"] = int(cookie["expiry"])
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"Skipping cookie error: {e}")
            self.driver.refresh()
            print("Cookies loaded. Attempting to access logged-in session.")
            sleep(5)
            return True
        return False

    def login(self, username, password):
        """
        Logs in to Facebook using the provided username and password.
        This method navigates to the Facebook login page, fills in the username
        and password fields, and clicks the login button. It also saves the cookies
        to a file for future sessions.
        """
        print("Logging in to Facebook...")
        try:
            self.driver.get(FacebookContants.LOGIN_URL.value)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            print("Login page loaded successfully Now I will perform login.")
            username_input_field = self.driver.find_element(By.ID, "email")
            password_input_field = self.driver.find_element(By.ID, "pass")

            print("Filing The Username field.")
            username_input_field.clear()
            username_input_field.send_keys(username)

            print("Filing The Password field.")
            password_input_field.clear()
            password_input_field.send_keys(password)

            print("Username and password fields filled successfully.")

            # Find and click login button
            self.driver.find_element("id", "loginbutton").click()
            print("Login button clicked.")

            # Wait for login to complete
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@placeholder='Search Facebook']")
                )
            )
            print("Login successful!")

            with open("fb_cookies.pkl", "wb") as f:
                pickle.dump(self.driver.get_cookies(), f)
            print("Cookies saved to 'fb_cookies.pkl'")
            sleep(3)
        except Exception as e:
            print(f"An error occurred during login: {e}")

    def get_search_input_field(self, search_keyword):
        """
        Waits for the search input field to be available and enters the search keyword.
        This method uses WebDriverWait to ensure the search input field is present
        before attempting to interact with it. It clears any existing text and enters
        the specified search keyword, then simulates pressing the Enter key to submit the search.
        """
        try:
            print("Waiting for the search input field to be available...")
            search_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@placeholder='Search Facebook']")
                )
            )
            print("Search input field found.")

            search_input.clear()
            search_input.send_keys(search_keyword)
            print(f"Search keyword '{search_keyword}' entered successfully.")

            search_input.send_keys(Keys.RETURN)
            print(f"Search results for '{search_keyword}' are now available.")
            sleep(3)
        except Exception as e:
            print(f"An error occurred while trying to find the search input field: {e}")

    def get_pages_button(self):
        """
        Waits for the 'Pages' button to be available and clicks it.
        This method uses WebDriverWait to ensure the 'Pages' button is clickable
        before attempting to click it. It handles both English and Spanish text
        for the button to accommodate different language settings.
        """
        print("Waiting for the 'Pages' button to be available...")
        try:
            pages_button = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//span[contains(text(),'Pages') or contains(text(),'Páginas')]",
                    )
                )
            )
            print("'Pages' button found. Clicking it now.")
            pages_button.click()
            print("Navigated to the 'Pages' section successfully.")
            sleep(3)
        except Exception as e:
            print(f"An error occurred while trying to find the 'Pages' button: {e}")

    def get_page_location_and_page_category(self):
        """Here we will wait for the page location and category elements to be available."""
        print("Waiting for the page location and category to be available...")
        try:
            # Wait for the page location and category elements to be present
            self.page_location = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//input[@placeholder='Location' or @placeholder='Ubicación']",
                    )
                )
            )
            self.page_category = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//span[contains(text(),'Category') or contains(text(),'Categoría')]",
                    )
                )
            )
            print("Page location and category found and saved")
        except Exception as e:
            print(
                f"An error occurred while trying to find the page location and category: {e}"
            )

    def search_pages_for_location_and_category(self, location):
        """"Searches for pages based on the specified location and category.
        This method clicks on the page location input field, enters the specified
        location, and attempts to select the first suggested location. It also clicks
        on the page category dropdown and selects the 'Any category' option.
        If the category dropdown is not found, it continues without applying a category filter."""
        print("Searching for pages based on location and category...")
        try:
            # Click on the page location input field
            self.page_location.click()
            sleep(1)

            print(f"Entering location: {location}")
            self.page_location.clear()
            self.page_location.send_keys(location)
            sleep(2)

            # Try to select the first suggested location
            try:
                location_exact = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "(//ul[contains(@aria-busy,'false')]/li[contains(@aria-selected,'false')])[1]",
                        )
                    )
                )
                location_exact.click()
            except Exception as err:
                print(
                    "Could not find location suggestions, continuing with entered text",
                    err,
                )

            # Click on the page category dropdown
            self.page_category.click()

            # Wait for the dropdown to become clickable
            try:
                category_type = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//span[contains(text(),'Any category') or contains(text(),'Cualquier categoría')]",
                        )
                    )
                )
                category_type.click()
            except Exception as err:
                print(
                    "Could not find category dropdown, continuing without category filter",
                    err,
                )

            sleep(2)
            print("Search completed successfully.")

        except Exception as e:
            print(f"An error occurred while searching for pages: {e}")

    def scroll_to_load_all_results(self, max_scrolls=10):
        """
        Scrolls the page to load all search results.
        This method scrolls down the page a specified number of times to ensure
        all results are loaded. It waits for a short period after each scroll
        to allow the page to load new content. If the end of the page is reached,
        it breaks out of the loop early.
        """
        print("Scrolling to load all results...")
        for scroll in range(max_scrolls):
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            sleep(2)
            # Check if we've reached the end
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == self.driver.execute_script(
                "return window.pageYOffset + window.innerHeight"
            ):
                break

    def request_page_details(self):
        """Requests the review detail page and collects all page links.
        This method waits for the search results to be loaded, scrolls to ensure
        all results are visible, and collects the links to the detail pages of
        the pages found in the search results. It removes duplicates from the list
        of detail pages and prints the total number of pages found."""

        print("Requesting Review Detail Page.")
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@aria-label,'Search results') or contains(@aria-label,'Resultados de búsqueda')]",
                    )
                )
            )
            print("Detail page loaded successfully.")

            # Scroll to load all results first
            self.scroll_to_load_all_results()

            # Get all page links
            self.detail_pages = [
                elem.get_attribute("href")
                for elem in self.driver.find_elements(
                    By.XPATH,
                    "//a[contains(@role,'presentation') and contains(@href,'/profile.php?id=') or contains(@href,'facebook.com/')]",
                )
                if elem.get_attribute("href")
                and "facebook.com" in elem.get_attribute("href")
            ]

            # Remove duplicates
            self.detail_pages = list(set(self.detail_pages))

            print(
                f"All results loaded successfully. Total {len(self.detail_pages)} pages found."
            )
        except Exception as error:
            print(f"Error While Requesting review detail page: {error}")

    def get_page(self, page_url):
        """
        Visits the specified page URL and attempts to click on the reviews button.
        This method navigates to the given page URL, waits for the reviews button
        to be clickable, and clicks it. It handles both English and Spanish text
        for the reviews button to accommodate different language settings. If the
        reviews button is not found, it prints an error message and returns False.
        Args:
            page_url (str): The URL of the Facebook page to visit.
        Returns:
            bool: True if the reviews page was opened successfully, False otherwise.
        """
        print(f"Visiting page: {page_url}")
        try:
            self.driver.get(page_url)
            sleep(3)

            # Try to find reviews button with different approaches
            try:
                # First try with English text
                reviews_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//span[contains(text(),'Reviews')]")
                    )
                )
            except Exception as err:
                try:
                    # Then try with Spanish text
                    print(f"Error While visiting Page :{page_url} Error:{err}")
                    reviews_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//span[contains(text(),'Reseñas')]")
                        )
                    )
                except Exception as err:
                    try:
                        reviews_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable(
                                (
                                    By.XPATH,
                                    "//a[@aria-label='Reviews' or @aria-label='Reseñas']",
                                )
                            )
                        )
                    except Exception as err:
                        print("No reviews button found for this page...", err)
                        return False

            if reviews_button:
                self.driver.execute_script("arguments[0].click();", reviews_button)
                print("Reviews button clicked. Now on the reviews page.")
                WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(
                        (
                            By.XPATH,
                            "//span[contains(@class,'x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x41vudc x1603h9y x1u7k74 x1xlr1w8 xzsf02u x1yc453h')]",
                        )
                    )
                )
                print("Reviews Page opened successfully.")
                return True
            else:
                print("No reviews button found on this page.")
                return False

            return False
        except Exception as e:
            print(f"Error while accessing page {page_url}: {e}")
            return False

    def get_review_details(self):
        """
        Extracts review details from the currently opened page.
        This method scrolls the page to load more reviews, waits for the review
        containers to be present, and extracts the reviewer's name and review text.
        It handles potential exceptions during the extraction process and returns
        a list of dictionaries containing the review details.
        Returns:
            list: A list of dictionaries containing review details.
        """
        print("Getting reviews Details.")
        reviews_data = []

        try:
            # Scroll to load more reviews
            last_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )
            scroll_attempts = 0

            while scroll_attempts < 5:  # Try scrolling 5 times max
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                sleep(3)
                new_height = self.driver.execute_script(
                    "return document.body.scrollHeight"
                )

                if new_height == last_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                last_height = new_height

            # Try different methods to find reviews
            try:
                review_containers = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_all_elements_located(
                        (
                            By.XPATH,
                            ".//div[contains(@class,'x1yztbdb x1n2onr6 xh8yej3 x1ja2u2z')]",
                        )
                    )
                )
            except Exception as err:
                try:
                    print("Primary review container not found:", err)
                    # Fallback to more general selector
                    review_containers = self.driver.find_elements(
                        By.XPATH, "//div[contains(@role,'article')]"
                    )
                except Exception as err:
                    print("Could not find any review containers", err)
                    return reviews_data

            print(f"Found {len(review_containers)} review containers")

            for index, review in enumerate(review_containers, start=1):
                print(f"Processing review {index} of {len(review_containers)}")
                try:
                    # Extract reviewer name
                    try:
                        review_elem = review.find_element(
                            By.XPATH,
                            ".//img[contains(@src,'https://static.xx.')]/parent::strong/preceding-sibling::strong//a",
                        )
                        reviewer_name = review_elem.text
                    except Exception as err:
                        print(
                            "Fallback: couldn't extract reviewer name from review block",
                            err,
                        )
                        reviewer_name = "Anonymous"

                    try:
                        review_text_elem = review.find_element(
                            By.XPATH, ".//div[contains(@dir,'auto')]"
                        )
                        if review_text_elem:
                            review_text = review_text_elem.text
                        else:
                            review_text = "No text found"
                    except TimeoutException:
                        print(
                            "Timed out waiting for review text to load.",
                            TimeoutException,
                        )
                        review_text = "No text found"  # Assign fallback value here
                    except Exception as e:
                        print(f"Error while getting the review text: {e}")
                        review_text = "No text found"

                    if review_text.strip() and review_text.lower() not in [
                        "no text found",
                        "anonymous",
                    ]:
                        scraped_data = {
                            "User_ID": str(uuid4()),
                            "Review_Name": reviewer_name.strip(),
                            "Review_Text": review_text.strip(),
                        }

                        validated_data = self.validate_data(scraped_data)
                        if validated_data:
                            reviews_data.append(validated_data)

                except Exception as e:
                    print(f"Error while processing a review: {e}")
                    continue

        except Exception as e:
            print(f"Error while getting review details: {e}")
        return reviews_data

    def snake_to_title(self, snake_str: str) -> str:
        """
        Converts a snake_case string to a title case string.

        Args:
            snake_str (str): The snake_case string.

        Returns:
            str: The title case string.
        """
        return snake_str.replace("_", " ")

    def validate_data(self, scraped_data):
        print("Validating scraped data...")
        try:
            review = Review(
                user_id=scraped_data["User_ID"],
                review_by=scraped_data["Review_Name"],
                comment=scraped_data["Review_Text"],
            )
            print("Data validation successful.")
            model_dict = review.model_dump()
            data_dict = {
                self.snake_to_title(key): value for key, value in model_dict.items()
            }
            return data_dict
        except Exception as e:
            print(f"Data validation failed: {e}")
            return None


def main():
    """Main function to run the scraper."""
    scraper = ReviewsScraper()
    database_manager = PostgresDBHandler()
    scraper.setup_driver()

    logged_in = scraper.load_cookies()
    if not logged_in:
        scraper.login(LoginCredentials.USERNAME.value, LoginCredentials.PASSWORD.value)
    else:
        print("Logged in using cookies. No need to login again.")

    search_keyword = "restuarants"
    scraper.get_search_input_field(search_keyword)

    scraper.get_pages_button()
    scraper.get_page_location_and_page_category()

    location = "islamabad"
    scraper.search_pages_for_location_and_category(location)

    scraper.request_page_details()

    for page_url in scraper.detail_pages[:10]:  # Limit to first 10 pages for testing
        print(f"Page URL: {page_url}")
        if scraper.get_page(page_url):
            data = scraper.get_review_details()
            print(f"Location Review Details: {data}")
            database_manager.connect()
            database_manager.ensure_table_exists()
            database_manager.insert_review(data)
        else:
            print(
                f"Skipping page: {page_url} as it has no reviews or couldn't be accessed."
            )
            continue
