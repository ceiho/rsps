''' This module contains the GitHubHarvester class
    see class doc for more information '''

import time
from datetime import datetime
import requests
from dateutil.relativedelta import relativedelta
from interfaces.repository_harvester import RepositoryHarvester
from interfaces.repository_complementer import RepositoryComplementer

class GitHubHarvester(RepositoryHarvester, RepositoryComplementer):
    '''

    .. class:: GitHubHarvester

    The GitHubHarvester class contains all mandatory methods to gather research
    software candidates, their Readme files and metadata. It may also be used
    for harvesting all repositories containing specific search terms.

    :param token: specifies the required rate_limit, search or core limit.
    :type token: str
    '''
    # URL to request the remaining rate limit
    RATE_REQUEST = 'https://api.github.com/rate_limit'
    # base GitHub REST API url
    BASE_URL = 'https://api.github.com/'
    # infix part to construct a search query
    SEARCH_INFIX = 'search/repositories?q='
    # sets the number of results per page to 100
    SUFFIX = '&per_page=100'
    # additional element to set the search interval in the query
    INFIX = '+created:'
    # list of file identifier in a repository that are no source code file. If a
    # repository contains only these file, it's not classified as research
    # software
    NON_SOURCE_CODE_FILES_IDENTIFIER = ['readme', 'license', 'gitignore']


    def _is_valid_api_token(self, token=None):
        '''
        The methods checks if the given authentication token is a valif one

        :param token: authentication token
        :type token: str
        :returns: flag whether token is valid.
        :rtype: bool
        '''
        if token:
            response = requests.get(
                self.RATE_REQUEST,
                headers={
                    'Authorization': 'token ' + token
                })

            if response.status_code == 200:
                return True

        return False


    def __init__(self, token=None):
        '''
        Constructor method
        '''

        # optional header for API request, but recommended by GitHub, sets the
        # response format to json and, if available, contains the
        # authentication token
        self.header_request = {
            'Accept': 'application/vnd.github.v3+json'
        }
        # optional header for API request regarding Readme files, sets the
        # response format to raw and, if available, contains the
        # authentication token
        self.header_readme = {
            'Accept': 'application/vnd.github.v3.raw'
        }
        if self._is_valid_api_token(token):
            self.header_request['Authorization'] = 'token ' + token
            self.header_readme['Authorization'] = 'token ' + token
            # Seconds to sleep between two search API calls
            self.sleep_search = 2
            # Seconds to sleep after a core API call, including requests for
            # commits, content, and Readme files
            self.sleep_core = 0.6
        else:
            # Seconds to sleep between two search API calls
            self.sleep_search = 6
            # Seconds to sleep after a core API call, including requests for
            # commits, content, and Readme files
            self.sleep_core = 60
            #print('No auth token defined, search requests are limited to 10',
            #      'per minute, other requests are limited to 60 per hour.')


    def get_search_sleep_time(self):
        '''
        The method returns the adapted sleep times for the GitHub REST API
        to generate a constant load. The rate limits are set as follows:
        search limit with token: 30 requests per minute
        search limit without token: 10 requests per minute

        Resulting in the following sleep times between two API calls:
        search with token: 2 seconds
        search without token: 7 seconds

        :returns: Sleep time in seconds.
        :rtype: float
        '''
        return self.sleep_search


    def get_core_sleep_time(self):
        '''
        The method returns the adapted sleep times for the GitHub REST API
        to generate a constant load. The rate limits are set as follows:
        core limit with token: 5000 requests per hour
        core limit wthout token: 60 requests per hour

        Resulting in the following sleep times between two API calls:
        core with token: 0.6 seconds
        core without token: 65 seconds

        :returns: Sleep time in seconds.
        :rtype: float
        '''
        return self.sleep_core


    def __check_rate_limit(self, header, mode, remaining_requests):
        '''
        The method returns the API rate limit for either
        the search requests or the core requests. If the rate limit
        limit is exhausted, the process sleeps for the time in seconds
        computed via the returned utc epoche seconds.

        :param header: header in json format for GitHub API calls.
        :type header: json object
        :param mode: specifies the required rate_limit, search or core limit.
        :type mode: str
        :param remaining_requests: number of remaining requests from
                                   previousAPI response.
        :type remaining_requests: int.
        :returns: None
        :rtype: None
        :raises: AttributeError, KeyError
        '''

        if remaining_requests in (-1, 0):
            response = requests.get(self.RATE_REQUEST, headers=header)
            utc = response.json()['resources'][mode]['reset']
            seconds = (utc - int(time.time())) + 2

            if response.json()['resources'][mode]['remaining'] == 0:
                print("waiting for rate limit reset in: ", seconds)
                time.sleep(seconds)


    def create_interval(self, start, end, delta):
        '''
        The generator method creates search intervals
        for the given period, the latest end date for the intervals is
        today and the generator stops.

        :param start: start date of the search period.
        :type start: str
        :param end: end date of the search period.
        :type end: str
        :param delta: size of the search intervals.
        :type delta: str
        :returns: time interval.
        :rtype: str
        :raises: ValueError.
        '''

        start_date = datetime.strptime(start, '%Y-%m-%d')
        fstr = 'relativedelta('+delta+')'
        now = datetime.now()
        if datetime.strptime(end, '%Y-%m-%d') < now:
            end_of_period = datetime.strptime(end, '%Y-%m-%d')
        else:
            end_of_period = now
        # if the period ends before it starts, break
        if start_date > end_of_period:
            print('The search period ends before it starts.')
            return
        if '=0' in delta:
            print('The time delta has to be a positive integer greater 0')
            return

        # begin search intervals of one day with the start date
        if delta == 'days=1':
            yield start

        while True:
            interval_end = start_date + eval(fstr)
            if delta == 'days=1':
                if (interval_end.date() == now.date()
                    or interval_end.date() == end_of_period):
                    yield datetime.strftime(interval_end, '%Y-%m-%d')
                    return
                yield datetime.strftime(interval_end, '%Y-%m-%d')
            else:
                end_date = interval_end+relativedelta(days=-1)
                if end_date >= end_of_period:
                    end_date = end_of_period
                    yield (datetime.strftime(start_date, '%Y-%m-%d')+'..' +
                           datetime.strftime(end_date, '%Y-%m-%d'))
                    return
                if end_date >= now:
                    end_date = now
                    yield (datetime.strftime(start_date, '%Y-%m-%d')+'..' +
                           datetime.strftime(end_date, '%Y-%m-%d'))
                    return
                yield (datetime.strftime(start_date, '%Y-%m-%d')+'..' +
                       datetime.strftime(end_date, '%Y-%m-%d'))
            start_date = interval_end


    def get_next_page(self, pages):
        '''
        The method extracts the url of the next page
        if the total count exceeds the limit of 100 results
        per page

        :param pages: a list of url pages.
        :type pages: [str]
        :returns: url of the next result page or None.
        :rtype: str
        :raises: ValueError.
        '''

        counter = 0
        # identifying next url
        while counter < len(pages):
            if (pages[counter].split(";")[1][6:10] == "next") and (counter == 0):
                # truncate url by "<" (first position)
                # and ">" (last position)
                return pages[counter].split(";")[0][1:-1]
            if (pages[counter].split(";")[1][6:10]) == "next":
                # truncate url by "blank <" (at the beginning)
                # and ">" (at the end)
                return pages[counter].split(";")[0][2:-1]
            if counter == (len(pages)-1):
                # no available next url
                return None
            counter = counter + 1


    def get_search_results(self, remaining_requests, next_url, key, interval):
        '''
        The methods constructs the search API call and requests the
        results from GitHub REST API.

        :param remaining_requests: Information about remaining requests from a
                                   preceding call or -1 if this information is
                                   not available.
        :type remaining_requests: int
        :param next_url: in the case of pagination the URL to request the
                         next page.
        :param next_url: in the case of pagination the URL to request the next page.
        :type next_url: str
        :param key: search term.
        :type key: str
        :param interval: search interval.
        :type interval: str
        :returns: A valid requests response or None.
        :rtype: requests.models.Response
        :raises: ValueError.
        '''
        if next_url:
            url = next_url
        else:
            url = self.BASE_URL + self.SEARCH_INFIX + \
                key + self.INFIX + interval + self.SUFFIX

        self.__check_rate_limit(self.header_request,
                              'search', remaining_requests)
        response = requests.get(url, headers=self.header_request)

        if response.status_code in [301, 302, 307]:
            next_url = response.headers['Location']
            response = requests.get(next_url, headers=self.header_request)
        elif response.status_code != 200:
            return None
        return response


    def __get_api_response_url(self, api_cat, name):
        '''
        The method constructs a GitHub REST API call.

        :param api_cat: specifies the required API call categorie.
        :type api_cat: str
        :param name: specified the user respectively repository name for
                     the API call.
        :type name: str
        :returns: URL or None.
        :rtype: str
        '''

        if api_cat == 'user':
            return self.BASE_URL + 'users/' + name + '/repos'
        if api_cat == 'metadata':
            return self.BASE_URL + 'repos/' + name
        if api_cat == 'content':
            return self.BASE_URL + 'repos/' + name + '/contents'
        if api_cat == 'commit':
            return self.BASE_URL + 'repos/' + name + '/commits?per_page=1'
        if api_cat == 'readme':
            return self.BASE_URL + 'repositories/' + name + '/readme'
        if api_cat == 'language':
            return self.BASE_URL + 'repos/' + name + '/languages'
        return None


    def get_api_response(self, api_cat, name, num_requests, url=None):
        '''
        The methods requests information from the GitHub REST API and checks
        the HTTPs response code. If the status code is ok (200), the response
        is returned. If a redirect occurs, the link is followed and the
        response returned. In all other cases None is returned.

        :param api_cat: API call categorie, including commits, content
                        and Readme files.
        :type api_cat: str
        :param name: User or repository name.
        :type name: str
        :param num_requests: Remaining requests, receied from a
                             preceding API call.
        :type num_requests: int
        :param url: Next API call, if available.
        :type url: str
        :returns: HTTPs response or None.
        :rtype: requests.models.Response
        '''

        self.__check_rate_limit(self.header_request, 'core', num_requests)
        header = self.header_readme if api_cat == 'readme' else self.header_request
        api_url = url if url else self.__get_api_response_url(api_cat, name)

        if api_url:
            response = requests.get(api_url, headers=header)

            if response.status_code in [301, 302, 307]:
                next_url = response.headers['Location']
                self.__check_rate_limit(self.header_request, 'core', int(
                    response.headers['X-Ratelimit-Remaining']))
                response = requests.get(next_url, headers=header)
                return response, int(response.headers['X-Ratelimit-Remaining'])

            if response.headers['status'] != '200 OK':
                return None, int(response.headers['X-Ratelimit-Remaining'])

            return response, int(response.headers['X-Ratelimit-Remaining'])

        return None, num_requests


    def has_no_possible_source_code_files(self, name, num_requests):
        '''
        The method checks whether a repository may be a source code repository.
        If it only contains a Readme file, a License file, and a .gitignore
        file, it is assumed that the respoitory is not a source code repository
        and False is returned, as well as the number of remaining requests for
        the next API call.

        :param name: Repository name.
        :type name: str
        :param num_requests: Remaining requests, received from a preceding
                             API call.
        :type num_requests: int
        :returns: flag indicating if repository may be a source code
                  repository, number of remaining requests
        :rtype: bool, int
        '''

        self.__check_rate_limit(self.header_request, 'core', num_requests)
        content, limit = self.get_api_response('content', name, num_requests)
        non_source_code_file_list = []

        if not content:
            return True, limit

        if len(self.NON_SOURCE_CODE_FILES_IDENTIFIER) >= len(content.json()):
            for non_source_file in self.NON_SOURCE_CODE_FILES_IDENTIFIER:
                for source_file in content.json():
                    if non_source_file in source_file['name'].lower():
                        non_source_code_file_list.append(source_file['name'])
            if len(non_source_code_file_list) == len(content.json()):
                return True, limit
            return False, limit
        return False, limit


    def get_first_commit(self, name, num_requests):
        '''
        The method requests the last commit and derives from the header the
        URL for the first commit to get its date. Returned are the flag of
        succesful request, the date of the first and last commit, as well as
        the number of remaining requestsf or the next API call.

        :param name: Repository name.
        :type name: str
        :param num_requests: Remaining requests.
        :type num_requests: int
        :returns: Succesful request flag, first commit date, last commit date,
                  remaining rate limit or None
        :rtype: bool, str, str, in
        '''

        self.__check_rate_limit(self.header_request, 'core', num_requests)
        response, limit = self.get_api_response('commit', name, num_requests)
        valid_json_list = True
        retries = 0
        first_commit_date = None
        last_commit_date = None

        if not response:
            return True, None, None, limit

        if response.headers['link']:
            self.__check_rate_limit(self.header_request, 'core', limit)
            while retries < 6:
                first_commmit = requests.get(
                    (response.headers['link'].split(" ")[2])[1:-2],
                    headers=self.header_request)
                if first_commmit.status_code == 500:
                    print('Server Error: waiting for 60 seconds and retrying ...')
                    time.sleep(60)
                    retries = retries + 1
                else:
                    break
            if isinstance(response.json(), list) and isinstance(first_commmit.json(), list):
                if self.keys_exists(response.json()[0], 'commit', 'author', 'date'):
                    last_commit_date = response.json(
                    )[0]['commit']['author']['date']
                else:
                    valid_json_list = False
                if self.keys_exists(first_commmit.json()[0], 'commit', 'author', 'date'):
                    first_commit_date = first_commmit.json(
                    )[0]['commit']['author']['date']
                else:
                    valid_json_list = False
            else:
                valid_json_list = False

            if valid_json_list:
                return False, first_commit_date, last_commit_date, limit

        return True, None, None, limit


    @staticmethod
    def keys_exists(element, *keys):
        '''
        Check if \*keys (nested) exists in `element` (dict).
        '''
        if not isinstance(element, dict):
            raise AttributeError(
                'keys_exists() expects dict as first argument.')
        if len(keys) == 0:
            raise AttributeError(
                'keys_exists() expects at least two arguments, one given.')

        _element = element
        for key in keys:
            try:
                _element = _element[key]
            except KeyError:
                return False
        return True
