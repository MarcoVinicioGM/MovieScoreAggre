from listscraper.scrape_functions import scrape_film

# The main function is not necessary if you only want to use one function from the library.
# Instead, you can directly import and use the specific function you need.

# Example usage:
# film_data = scrape_film("https://letterboxd.com/film/inception/", ".json")
# print(film_data)

# If you need to use this file as a script entry point, you can keep a simplified version:
if __name__ == "__main__":
    print("This module is intended to be imported, not run directly.")
    print("Example usage: from listscraper.scrape_functions import scrape_film")