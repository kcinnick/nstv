"""
Debug NZBGeek movie search for "2001 A Space Odyssey"
"""
import os
import django
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
django.setup()

from nstv.download import NZBGeek
from nstv.models import Movie

# Test movie name
movie_name = "The Artist (2011)"

print(f"Testing movie search for: {movie_name}")
print("=" * 80)

# Create NZBGeek instance and login
nzbgeek = NZBGeek()
nzbgeek.login()

# Build the search URL (same as get_gid_for_movie)
url = f"https://nzbgeek.info/geekseek.php?moviesgeekseek=1&c=2000&browseincludewords={movie_name}".replace(" ", "%20")
print(f"Search URL: {url}\n")

# Get the results
r = nzbgeek.session.get(url)
soup = BeautifulSoup(r.content, "html.parser")

# Check for results
geekseek_results = soup.find('div', class_='geekseek_results')
if geekseek_results and 'returned 0' in geekseek_results.text:
    print("No results found")
else:
    print("Found results!\n")
    
    # Find all release tables
    releases_tables = soup.find_all("table", class_="releases")
    print(f"Found {len(releases_tables)} release tables\n")
    
    # Just look at the first result in detail
    if releases_tables:
        first_table = releases_tables[0]
        print("First result - Full structure:")
        print("-" * 80)
        
        all_tds = first_table.find_all('td')
        for idx, td in enumerate(all_tds):
            td_classes = td.get('class', [])
            td_text = td.text.strip()[:100]
            print(f"  TD #{idx}: class={td_classes}, text='{td_text}'")
        
        print("\n" + "-" * 80)
        print("Looking for movieid link...")
        all_links = first_table.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            if 'movieid=' in href:
                print(f"  Found: {href}")
                print(f"  Link text: '{link.text.strip()}'")
                print(f"  Link parent: {link.parent.name}, parent class: {link.parent.get('class')}")
