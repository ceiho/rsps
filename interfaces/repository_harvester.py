''' Interface for repository harvester classes '''

import abc
import requests

class RepositoryHarvester(metaclass=abc.ABCMeta):
    '''

    .. class:: RepositoryHarvester

    Defines the signature operations for repository harvester classes.
    '''

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_search_sleep_time') and
                callable(subclass.get_search_sleep_time) and

                hasattr(subclass, 'get_core_sleep_time') and
                callable(subclass.get_core_sleep_time) and

                hasattr(subclass, 'create_interval') and
                callable(subclass.create_interval) and

                hasattr(subclass, 'get_next_page') and
                callable(subclass.get_next_page) and

                hasattr(subclass, 'get_search_results') and
                callable(subclass.get_search_results) and

                hasattr(subclass, 'get_api_response') and
                callable(subclass.get_api_response) or
                NotImplemented)


    @abc.abstractmethod
    def get_search_sleep_time(self) -> float:
        '''
        The method returns the sleep times between two search requests.
        :returns: Sleep time in seconds.
        :rtype: float
        '''
        raise NotImplementedError


    @abc.abstractmethod
    def get_core_sleep_time(self) -> float:
        '''
        The method returns the sleep time in seconds

        :returns: Sleep time in seconds.
        :rtype: float
        '''
        raise NotImplementedError


    @abc.abstractmethod
    def create_interval(self, start: str, end: str, delta: str) -> str:
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
        raise NotImplementedError


    @abc.abstractmethod
    def get_next_page(self, pages: [str]) -> str:
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
        raise NotImplementedError


    @abc.abstractmethod
    def get_search_results(self, remaining_requests: int, next_url: str,
                           key: str, interval: str) -> requests.models.Response:
        '''
        The methods constructs the search API call and requests the results.

        :param remaining_requests: Information about remaining requests from a preceding
                                   call or -1 if this information is not available.
        :type remaining_requests: int
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
        raise NotImplementedError


    @abc.abstractmethod
    def get_api_response(self, api_cat: str, name: str,
                         num_requests: int, url: str) -> requests.models.Response:
        '''
        The methods requests information from a REST API and checks the HTTPs response code.
        If the status code is ok (200), the response is returned. If a redirect occurs, the
        link is followed and the response returned. In all other cases None is returned.

        :param api_cat: API call categorie, including commits, content, and Readme files.
        :type api_cat: str
        :param name: User or repository name.
        :type name: str
        :param num_requests: Remaining requests, receied from a preceding API call.
        :type num_requests: int
        :param url: Next API call, if available.
        :type url: str
        :returns: HTTPs response or None.
        :rtype: requests.models.Response
        '''
        raise NotImplementedError
 