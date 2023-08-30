
from bs4 import BeautifulSoup
from lingua import Language, LanguageDetectorBuilder
import requests
from string import Template
from urllib.parse import urljoin

languages = [Language.ENGLISH, Language.FRENCH, Language.SPANISH, Language.ITALIAN, Language.GERMAN, Language.DUTCH, Language.PORTUGUESE, Language.FINNISH, Language.DANISH, Language.SWEDISH]
detector = LanguageDetectorBuilder.from_languages(*languages).build()


def check_text_in_english(text):

    english_detection_confidence = detector.detect_language_of(text)
    return english_detection_confidence == Language.ENGLISH

def get_stars_from_rating_string(rating_string):
    return int(''.join([char for char in rating_string if char.isdigit()])) / 2

def get_page_url_comp(base_url, base_page_url, page_no):
    if page_no == 1:
        page_url_comp = base_url
    else:

        page_url_comp = urljoin(base_url, base_page_url.format(page=str(page_no)))
    return page_url_comp

class FilmData:
    def __init__(self, film, url_film_title, year, directors, genres, themes):
        self.film = film
        self.url_film_title = url_film_title
        self.year = year
        self.directors = directors
        self.genres = genres
        self.themes = themes
class FilmReview:
    def __init__(self, film, url_film_title, user, rating, review_text):
        self.film = film
        self.url_film_title = url_film_title
        self.user = user
        self.rating = rating
        self.review_text = review_text

    def asdict(self):
        return {'film': self.film, 'user': self.user, 'rating': self.rating, 'review_text': self.review_text}

    def __repr__(self):
        return f'Film: {self.film} \n User: {self.user} \n Rating: {self.rating} \n Review text: {self.review_text}'

BASE_REV_URL = 'reviews/by/added'
BASE_LB_URL = 'https://letterboxd.com'
CREW_URL_SUFFIX = 'crew'
GENRES_URL_SUFFIX = 'genres'
SHOW_ALL_THEMES_TEXT = 'Show All…'

base_page_url = 'page/{page}'
base_film_url = 'https://letterboxd.com/film/{film}'
base_list_url = '{user}/list/{list_name}'
def fetch_html(url):
    return requests.get(url)
def get_page_content(page):
    return BeautifulSoup(page.content, 'html.parser')
class ListScraper:
    def __init__(self, user, list_name):
        self.user = user
        self.list_name = list_name
        self.list_url = urljoin(BASE_LB_URL, base_list_url.format(user=self.user, list_name=self.list_name))
        self.url_film_titles = []

    def get_film_names(self):
        page_no = 1
        pages_empty = False
        while pages_empty == False:

            page_url_comp = get_page_url_comp(self.list_url, base_page_url, page_no)
            page_url = urljoin(self.list_url, page_url_comp)
            page = fetch_html(page_url)
            soup = get_page_content(page)
            results = soup.find('ul', class_='poster-list')
            try:
                page_posters = results.find_all('div', class_='film-poster')
            except AttributeError:
                pages_empty = True
                break

            if page_posters and page.status_code == 200:
                for poster_element in page_posters:
                    url_film_title = poster_element['data-film-slug']
                    self.url_film_titles.append(url_film_title)
                page_no += 1
            else:
                pages_empty = True
    def scrape_film_metadata(self):
        for url_film_title in self.url_film_titles:
            metadata_scraper = FilmDataScraper(url_film_title)
            metadata_scraper.scrape_metadata()
            metadata_scraper.scrape_genres()
    def scrape_film_reviews(self):
        pass


lscraper = ListScraper('jabzie_crockett', 'friday-funday')
lscraper.get_film_names()
print(1)
class FilmScraper:
    def __init__(self, url_film_title):
        self.url_film_title = url_film_title
        self.base_film_url = base_film_url.format(film=self.url_film_title)

    def get_tab_url(self, url_suffix):
        return urljoin(self.base_film_url, url_suffix)

class FilmDataScraper(FilmScraper):

    def __init__(self, url_film_title):
        super().__init__(url_film_title)

        self.full_title = ''
        self.year = 0
        self.directors = []
        self.genres = []
        self.themes = []

    def scrape_metadata(self):

        crew_url = self.get_tab_url(CREW_URL_SUFFIX)
        page = fetch_html(crew_url)
        soup = get_page_content(page)
        header_results = soup.find(id='featured-film-header')
        full_title = header_results.find('h1', class_='headline-1').text
        year = int(header_results.find('small', class_='number').find('a').text)
        crew_results = soup.find('div', id='tab-crew').find('div', class_='text-sluglist')
        directors_results = crew_results.find_all('a', class_='text-slug')
        directors = [directors_result.text for directors_result in directors_results]

        self.full_title = full_title
        self.year = year
        self.directors = directors

    def scrape_genres(self):
        genres_url = self.get_tab_url(GENRES_URL_SUFFIX)
        page = fetch_html(genres_url)
        soup = get_page_content(page)
        genres_themes_div = soup.find('div', id='tab-genres')
        genres_results = genres_themes_div.find('div', class_='text-sluglist')
        genres = [genre.text for genre in genres_results.find_all('a', class_='text-slug')]
        themes_results = genres_results.find_next_sibling('div', class_='text-sluglist')
        try:
            themes = [theme.text for theme in themes_results.find_all('a', class_='text-slug') if theme.text != SHOW_ALL_THEMES_TEXT]
            self.themes = themes
        except AttributeError:
            self.themes = None

        self.genres = genres



class FilmReviewScraper(FilmScraper):
    def __init__(self, url_film_title):
        super().__init__(url_film_title)
        self.review_list = []
    def scrape_reviews(self, page_limit=None):

        page_no = 1
        pages_empty = False
        while pages_empty == False:

            page_url_comp = get_page_url_comp(BASE_REV_URL, base_page_url, page_no)
            page_url = urljoin(self.base_film_url, page_url_comp)
            page = fetch_html(page_url)
            soup = get_page_content(page)
            results = soup.find(class_='viewings-list')
            page_reviews = results.find_all(class_='film-detail-content')

            if page_reviews:
                for review_element in page_reviews[1:]:
                    attribution = review_element.find('p', class_='attribution')
                    user_element = review_element.find('strong', class_='name').text
                    rating_element = attribution.find('span', class_='rating')
                    try:
                        star_rating = \
                        [get_stars_from_rating_string(class_) for class_ in rating_element.attrs['class'] if
                         any(str.isdigit(char) for char in class_)][0]
                    except AttributeError:
                        star_rating = None
                    review_text = review_element.find('div', class_='body-text').text
                    user_review = FilmReview(user_element, star_rating, review_text)
                    self.review_list.append(user_review)
                page_no += 1
            else:
                pages_empty = True

film = 'green-snake'
fds = FilmDataScraper(film)
fds.scrape_metadata()
fds.scrape_genres()
frs = FilmReviewScraper(film)
frs.scrape_reviews()
print(1)

if __name__ == '__main__':
    film_list = ['spirited-away', 'come-and-see', 'green-snake', 'suspiria', 'female-trouble', 'salo']
    for film in film_list:
        scraper = FilmReviewScraper(film)
        review_list = scraper.scrape_reviews()
