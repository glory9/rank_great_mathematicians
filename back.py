from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json

def log_error(e):
    """
    This function prints errors
    """
    # store errors in log file
    # with closing(open("error_log", "a")) as err:
    #     err.write(e)

    print(e)

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            )

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {} : {}'.format(url, str(e)))
        return None

def get_names():
    """
    Downloads the page where the list of mathematicians is found
    and returns a list of strings, one per mathematician
    """
    url = 'http://www.fabpedigree.com/james/mathmen.htm'
    response = simple_get(url)

    if response:
        html = BeautifulSoup(response, 'html.parser')
        names = set()
        for li in html.select('li'):
            for name in li.text.split('\n'):
                if len(name) > 0:
                    names.add(name.strip())
        return list(names)

    # Raise an exception if we failed to get any data from the url
    raise Exception('Error retrieving contents at {}'.format(url))

def get_hits_on_name(name):
    """
    Remove middle names so url can be compatible with API endpoint
    """

    split = name.split(" ")
    if len(split) > 2:
        name = " ".join([split[0], split[-1]])

    """
    Accepts a `name` of a mathematician and returns the number of
    all-time hits that a mathematician's Wikipedia page has received
    as an `int`
    """
    # Makes a call to the {} API
    url_root = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/all-agents/{}/monthly/20150101/20200501"

    response = simple_get(url_root.format(name))

    if response:
        js = json.loads(response)
        view_count = 0
        for month in js["items"]:
            view_count += month["views"]

        return view_count

    log_error('No pageviews found for {}'.format(name))
    return None

if __name__ == '__main__':
    print('Getting the list of the world\'s greatest mathematicians....')
    names = get_names()
    print('... done.\n')

    results = []

    print('Getting stats for each name....')

    for name in names:
        try:
            hits = get_hits_on_name(name)
            if hits is None:
                hits = -1
            results.append((hits, name))
        except:
            results.append((-1, name))
            log_error('error encountered while processing '
                      '{}, skipping'.format(name))

    print('... done.\n')

    results.sort(reverse=True)

    if len(results) > 5:
        top_marks = results[:5]
    else:
        top_marks = results

    print('\nThe most popular mathematicians are:\n')
    for (mark, mathematician) in top_marks:
        print('{} with {} pageviews'.format(mathematician, mark))

    no_results = len([res for res in results if res[0] == -1])
    print('\nBut we did not find results for '
          '{} mathematicians on the list'.format(no_results))
