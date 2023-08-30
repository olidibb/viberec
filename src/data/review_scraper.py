
from bs4 import BeautifulSoup
from lingua import Language, LanguageDetectorBuilder
import requests
from string import Template

languages = [Language.ENGLISH, Language.FRENCH, Language.SPANISH, Language.ITALIAN, Language.GERMAN, Language.DUTCH, Language.PORTUGUESE, Language.FINNISH, Language.DANISH, Language.SWEDISH]
detector = LanguageDetectorBuilder.from_languages(*languages).build()


def check_text_in_english(text):

    english_detection_confidence = detector.detect_language_of(text)
    return english_detection_confidence == Language.ENGLISH

def get_stars_from_rating_string(rating_string):
    return int(''.join([char for char in rating_string if char.isdigit()])) / 2

class UserReview:
    def __init__(self, user, rating, review_text):
        self.user = user
        self.rating = rating
        self.review_text = review_text

    def asdict(self):
        return {'user': self.user, 'rating': self.rating, 'review_text': self.review_text}

    def __repr__(self):
        return f'User: {self.user} \n Rating: {self.rating} \n Review text: {self.review_text}'


BASE_URL = Template('https://letterboxd.com/film/$film/reviews/by/added/page/$page')


class FilmReviewScraper:
    def __init__(self, url_film_title):
        self.url_film_title = url_film_title
        self.review_list = []
    def scrape_reviews(self, page_limit=None):

        page_no = 1
        pages_empty = False
        while pages_empty == False:
            page_url = BASE_URL.substitute(film=self.url_film_title, page=page_no)
            page = requests.get(page_url)
            soup = BeautifulSoup(page.content, 'html.parser')
            results = soup.find(class_='viewings-list')
            page_reviews = results.find_all(class_='url_film_title-detail-content')

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
                    user_review = UserReview(user_element, star_rating, review_text)
                    self.review_list.append(user_review)
                page_no += 1
            else:
                pages_empty = True

        return self.review_list


if __name__ == '__main__':
    film_list = ['spirited-away', 'come-and-see', 'green-snake', 'suspiria', 'female-trouble', 'salo']
    for film in film_list:
        scraper = FilmReviewScraper(film)
        review_list = scraper.scrape_reviews()
#
# film = 'spirited-away'
# review_list = []
# URL = f'https://letterboxd.com/film/{film}/reviews/by/added/page/'
# page_no = 1
# pages_empty = False
# while pages_empty == False and page_no <=10:
#     full_URL = URL + str(page_no)
#     page = requests.get(full_URL)
#     soup = BeautifulSoup(page.content, 'html.parser')
#     results = soup.find(class_='viewings-list')
#     page_reviews = results.find_all(class_='film-detail-content')
#
#     if page_reviews:
#         for review_element in page_reviews[1:]:
#             attribution = review_element.find('p', class_='attribution')
#             user_element = review_element.find('strong', class_='name').text
#             rating_element = attribution.find('span', class_='rating')
#             try:
#                 star_rating = [get_stars_from_rating_string(class_) for class_ in rating_element.attrs['class'] if any(str.isdigit(char) for char in class_)][0]
#             except AttributeError:
#                 star_rating = None
#             review_text = review_element.find('div', class_='body-text').text
#             review_obj = UserReview(user_element, star_rating, review_text)
#             review_list.append(review_obj)
#         page_no += 1
#     else:
#         pages_empty = True
#         print(f'{film.capitalize()} reviews scraped over {page_no - 1} pages')
#
# # review_text_list = [review.review_text for review in review_list if review.english_confidence > 0.5]
# # pickle.dump(review_text_list, file=open('cas_test_reviews.pkl', 'wb'))
# for review in review_list:
#     print(review)
#     print('\n \n \n')