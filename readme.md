<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/5/51/Facebook_f_logo_%282019%29.svg" alt="Facebook Logo" width="100">
</p>

<h1 align="center">📄 Facebook Reviews Scraper</h1>

<p align="center">
  A Python-based scraper that logs into Facebook and extracts page reviews using Selenium, storing them in a PostgreSQL database.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Selenium-Automation-brightgreen.svg" alt="Selenium">
  <img src="https://img.shields.io/badge/PostgreSQL-Database-blue.svg" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Made%20with-❤️%20in%20Python-red.svg" alt="Made with Python">
</p>


---


## 🚀 Features

- ✅ Facebook login via Selenium
- ✅ Scrapes user reviews from Facebook pages
- ✅ Extracts reviewer name, rating, review text, and timestamps
- ✅ Stores data in a PostgreSQL database
- ✅ Customizable and extendable codebase

---

## 🛠️ Tech Stack

| Tool       | Description                                        |
|------------|----------------------------------------------------|
| **Python** | Core language used for scripting and automation    |
| **Selenium** | Automates web browser interaction for scraping dynamic content |
| **PostgreSQL** | Relational database used to store scraped reviews |
| **psycopg2** | PostgreSQL adapter for Python                    |

---

## 🔐 Prerequisites

- Python 3.8+
- Google Chrome + ChromeDriver (Ensure version compatibility)
- Facebook credentials (your own account with access)
- PostgreSQL server running

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/facebook-review-scraper.git
cd facebook-review-scraper

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt


⚙️ Configuration
Create a .env file in the root directory:

FB_EMAIL=your_facebook_email
FB_PASSWORD=your_facebook_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=facebook_reviews
DB_USER=your_db_user
DB_PASSWORD=your_db_password


🗃️ Sample Output
{
  "reviewer_name": "John Doe",
  "rating": 5,
  "review_text": "Excellent service and great content!",
  "review_date": "2023-07-18"
}

📬 Contact
Email: shujaatalee888@gmail.com

made with ❤️ by Shujaat
