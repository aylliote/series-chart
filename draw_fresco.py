import bs4

from urllib.request import Request, urlopen

import matplotlib.pyplot as plt
import matplotlib
%matplotlib inline
## plt.style.use('ggplot')

#from tqdm import tqdm
import numpy as np
import re


_cdict = {'red':   ((0.0,  1.0, 1.0),
                    (0.2,  0.80, 0.80),
                    (0.4,  0.60, 0.60),
                    (0.6, 0.40, 0.40),
                    (0.8, 0.20, 0.20),
                    (1.0,  0.00, 0.00)),

          'green': ((0.0,  0.00, 0.00),
                    (0.2,  0.20, 0.20),
                    (0.4,  0.40, 0.40),
                    (0.6, 0.60, 0.60),
                    (0.8, 0.80, 0.80),
                    (1.0,  1.0, 1.0)),

          'blue':  ((0.0,  0.0, 0.0),
                    (0.5,  0.0, 0.0),
                    (1.0,  0.0, 0.0))}

_my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap', _cdict, 256)


def load_soup(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urlopen(req).read()
    soup = bs4.BeautifulSoup(html, "html5lib")
    return soup


def linear_transform(r):
    return r / 10


def display_fresk(ratings):
    _ratings = [linear_transform(e) for e in ratings]
    _bounds = [(e, _ratings[ix + 1])
              for ix, e in enumerate(_ratings) if ix != (len(_ratings) - 1)]
    fresk_mat = np.outer(np.ones(100), np.hstack(
        [np.linspace(e[0], e[1], 100) for e in _bounds]))

    plt.figure(figsize=(50, 8))
    plt.imshow(fresk_mat, aspect='auto', cmap=_my_cmap)
    plt.show()
    plt.close()
    
    
def crawl_series(url, draw_curve = True, draw_fresk = True, print_ratings=False):
    soup = load_soup(url)
    
    try:
        n_seasons = int([e for e in soup.find('div', attrs = {"class": "seasons-and-year-nav"}).children][7].find('a').text)
    except KeyError:
        print(' Could not find the number of seasons')
        
    name_series = soup.find("h1", attrs = {"itemprop": "name"}).text.strip()
        
    __ratings = []
    
    for i in range(n_seasons):
        soup = load_soup(url + '/episodes?season=' + str(i+1))
        
        episodes = soup.findAll("div", attrs = {"class": ["list_item even", "list_item odd"]})

        __ratings += [float(e.find("span", attrs = {"class": 'ipl-rating-star__rating'}).text) for e in \
                     episodes if e.find("span", attrs = {"class": "ipl-rating-star__total-votes"}) is not None]

    dict_ratings = {k+1:v for k,v in enumerate(__ratings)}
    
    print('\n')
    print('\n')
    print(name_series.upper().center(124, ' '))
    
    if draw_curve:
        #plt.figure(figsize=(50, 15))
        plt.plot(dict_ratings.keys(), dict_ratings.values())
        plt.xlabel('Episode')
        plt.ylabel('Rating')
        #plt.title(name_series)
        plt.show()
        plt.close()
    
    if draw_fresk:
        display_fresk(dict_ratings.values())
        
    if print_ratings:
        print(list(dict_ratings.values()))
    
    #return dict_ratings

def main():
    main_url = "http://www.imdb.com/chart/toptv"
    soup = load_soup(main_url)
    series_idx = [re.search(r'/[a-z0-9]+/\?', e.find('a')['href']).group()[1:-2] for e in \
                  soup.findAll("td", attrs = {'class': "titleColumn"})]

    for _ix in series_idx:
        crawl_series("http://www.imdb.com/title/"+_ix)


if __name__ == "__main__":
    main()