class RestaurantDetails:
    def __init__(self, url, rating, price_range, cuisine, meals, location, google_maps_link, website, email, phone_number):
        self.url = url
        self.rating = rating
        self.price_range = price_range
        self.cuisine = cuisine
        self.meals = meals
        self.location = location
        self.google_maps_link = google_maps_link
        self.website = website
        self.email = email
        self.phone_number = phone_number

    def to_dict(self):
        return {
            "URL": self.url,
            "Rating": self.rating,
            "Price Range": self.price_range,
            "Cuisine": self.cuisine,
            "Meals": self.meals,
            "Location": self.location,
            "Google Maps Link": self.google_maps_link,
            "Website": self.website,
            "Email": self.email,
            "Phone Number": self.phone_number
        }
        
    def print_details(self):
        print(f"Restaurant Details:")
        print(f"    URL: {self.url}")
        print(f"    Rating: {self.rating}")
        print(f"    Price Range: {self.price_range}")
        print(f"    Cuisine: {self.cuisine}")
        print(f"    Meals: {self.meals}")
        print(f"    Location: {self.location}")
        print(f"    Google Maps Link: {self.google_maps_link}")
        print(f"    Website: {self.website}")
        print(f"    Email: {self.email}")
        print(f"    Phone Number: {self.phone_number}")
