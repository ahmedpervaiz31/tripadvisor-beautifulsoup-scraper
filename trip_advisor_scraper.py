import os
import json
import time
import requests
from bs4 import BeautifulSoup
from restaurant import RestaurantDetails

class RestaurantScraper:
    def __init__(self, api_key, scraperapi_url):
        self.api_key = api_key
        self.scraperapi_url = scraperapi_url
        self.headers = {    
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.city_links_file = 'city_links.txt'
        self.restaurant_links_file = 'restaurant_links.txt'
        self.restaurant_details_file = 'restaurant_details.json'
        
        self.trip_advisor_url = 'https://www.tripadvisor.com'
    
    def engine(self):
        # if city or restaurant links already scraped
        # then dont scrape again - to save memory
        if os.path.exists(self.city_links_file) and os.stat(self.city_links_file).st_size > 2:
            print("Skipping scraping cities.")
        else:
            print("Scraping cities...")
            self.scrape_cities()
        
        if os.path.exists(self.restaurant_links_file) and os.stat(self.restaurant_links_file).st_size > 2:
            print("Skipping scraping restaurants.")
        else:
            print("Scraping restaurants...")
            self.scrape_restaurants()
                
        self.scrape_details()
    
    def generate_payload(self, url):
        payload = {
                'api_key': self.api_key,
                'url': url,
                'keep_headers': 'true'
            }
        return payload
    
    def store_json(self, data, file_name):
        with open(file_name, 'w') as fd:
            json.dump(data, fd, indent=4)
        
    def scrape_pages(self, url, page):
        payload = self.generate_payload(url)
        
        r = requests.get(self.scraperapi_url, params=payload, headers=self.headers)
        
        if r.status_code != 200:
            print(f"Request failed with status code: {r.status_code}")
            return
        
        soup = BeautifulSoup(r.text, 'html.parser')
        city_url = ''
        
        with open(self.city_links_file, 'a') as fd:
            if page == 1:
                # Scraping page 1
                geo_name_links = soup.select('div.geo_name a')
                
                for a_tag in geo_name_links:
                    if 'href' in a_tag.attrs:
                        city_url = a_tag['href']
                        fd.write(city_url + '\n')
                        print(city_url)
            else:
                # Scraping subsequent pages
                ul = soup.find("ul", class_="geoList")
                
                li_elements = ul.find_all("li")
                
                for li in li_elements:
                    a_tag = li.find('a')
                    if a_tag and 'href' in a_tag.attrs:
                        city_url = a_tag['href']
                        fd.write(city_url + '\n')
                        print(city_url)
                        
            
            
        time.sleep(1)
    
    def scrape_cities(self):
        city_links = []
        # Scrape page 1 
        initial_url = 'https://www.tripadvisor.com/Restaurants-g28926-California.html'
        print("Scraping page 1...")
        self.scrape_pages(initial_url, 1)

        # Scrape following pages till page 3
        for page in range(2, 4):
            offset = (page - 1) * 20
            next_url = f'https://www.tripadvisor.com/Restaurants-g28926-oa{offset}-California.html'
            print(f"\nScraping page {page}...")
            self.scrape_pages(next_url, page)
            
    def scrape_restaurants(self):
        max_city = 3 # for testing
        count = 0
        
        with open(self.city_links_file, 'r') as fd:
            city_links = [line.strip() for line in fd.readlines()]
            
        with open(self.restaurant_links_file, 'a') as fd:
            for city in city_links:
                if count >= max_city:
                    break
                
                url = self.trip_advisor_url + city
                
                payload = self.generate_payload(url)
                r = requests.get(self.scraperapi_url, params=payload, headers=self.headers)
                
                if r.status_code != 200:
                    print(f"Request failed with status code: {r.status_code}")
                    return
                
                soup = BeautifulSoup(r.text, 'html.parser')
                
                restaurant_links_divs = soup.select('div.biGQs._P.fiohW.alXOW.NwcxK.GzNcM.ytVPx.UTQMg.RnEEZ.ngXxk')
                
                for div in restaurant_links_divs:
                    a_tag = div.find('a', class_='BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS')
                    
                    if a_tag and 'href' in a_tag.attrs:
                        restaurant_url = a_tag['href']
                        
                        fd.write(restaurant_url + '\n')
                        print(restaurant_url)
                count += 1
                time.sleep(1)
            
            
    def scrape_details(self):
        RestaurantList = []

        with open(self.restaurant_links_file) as fd:
            restaurant_links = [line.strip() for line in fd.readlines()]

        for restaurant in restaurant_links:
            url = self.trip_advisor_url + restaurant
            
            payload = self.generate_payload(url)
            r = requests.get(self.scraperapi_url, params=payload, headers=self.headers)
            
            if r.status_code != 200:
                print(f"Request failed for {url} with status code: {r.status_code}")
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')

            rating = self.extract_rating(soup)
            price_range, cuisine, meals = self.extract_details(soup)
            location, google_maps_link = self.extract_location(soup)
            website = self.extract_website(soup)
            email = self.extract_email(soup)
            phone_number = self.extract_phone_number(soup)

            restaurant_obj = RestaurantDetails(
                url, rating, price_range, cuisine, meals, location, google_maps_link, website, email, phone_number
            )
            restaurant_obj.print_details()

            RestaurantList.append(restaurant_obj.to_dict())

            time.sleep(1)

        self.store_json(RestaurantList, 'restaurant_details.json')

    def extract_rating(self, soup):
        rating_container = soup.find('div', class_='biGQs _P fiohW ngXxk')
        if rating_container:
            rating_div = rating_container.find_next_sibling('div', class_='sOyfn u f K')
            if rating_div:
                span = rating_div.find('span', class_='biGQs _P fiohW uuBRH')
                if span:
                    return span.text.strip()
        print("Rating not found.")
        return "N/A"

    def extract_details(self, soup):
        detail_divs = soup.find_all('div', class_="biGQs _P pZUbB alXOW oCpZu GzNcM nvOhm UTQMg ZTpaU W hmDzD")
        if len(detail_divs) > 2:
            price_range = detail_divs[0].text.strip()
            cuisine = detail_divs[1].text.strip()
            meals = detail_divs[2].text.strip()
            return price_range, cuisine, meals
        print("Details not found.")
        return "N/A", "N/A", "N/A"

    def extract_location(self, soup):
        location_div = soup.find('div', class_='hpxwy e j')
        if location_div:
            location_link = location_div.find('a', class_="BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS")
            if location_link and 'href' in location_link.attrs:
                google_maps_link = location_link['href']
                location_span = location_link.find('span', class_='biGQs _P pZUbB hmDzD')
                if location_span:
                    location = location_span.text.strip()
                    return location, google_maps_link
        print("Location or Google Maps link not found.")
        return "N/A", "N/A"

    def extract_website(self, soup):
        website_link = soup.find('a', href=lambda href: href and href.startswith('www.'))
        if website_link:
            return website_link['href'].strip()
        print("Website not found.")
        return "N/A"

    def extract_email(self, soup):
        email_link = soup.find('a', href=lambda href: href and href.startswith('mailto:'))
        if email_link:
            return email_link['href'].replace('mailto:', '').strip()
        print("Email not found.")
        return "N/A"

    def extract_phone_number(self, soup):
        phone_link = soup.find('a', href=lambda href: href and href.startswith('tel:'))
        if phone_link:
            return phone_link['href'].replace('tel:', '').strip()
        print("Phone number not found.")
        return "N/A"
        
if __name__ == "__main__":
    api_key = '5116d8272d3452283b011e9b4c578bf5'
    scraperapi_url = 'https://api.scraperapi.com/'
    scraper = RestaurantScraper(api_key, scraperapi_url)
    scraper.engine()