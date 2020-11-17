''' Interface for repository complementer classes '''

import abc
import requests

class RepositoryComplementer(metaclass=abc.ABCMeta):
    '''

    .. class:: RepositoryComplementer

    Defines the signature operations for repository complementer classes.
    '''

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'get_api_response') and
                callable(subclass.get_api_response) and

                hasattr(subclass, 'has_no_possible_source_code_files') and
                callable(subclass.has_no_possible_source_code_files) and

                hasattr(subclass, 'get_first_commit') and
                callable(subclass.get_first_commit) or
                NotImplemented)


    @abc.abstractmethod
    def get_api_response(self, api_cat: str, name: str,
                         num_requests: int, url: str) -> requests.models.Response:
        '''
        The methods requests information from a REST API and checks the
        HTTPs response code. If the status code is ok (200),
        the response is returned. If a redirect occurs, the link is
        followed and the response returned. In all other cases None is returned.

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


    @abc.abstractmethod
    def has_no_possible_source_code_files(self, name: str,
                                          num_requests: int) -> (bool, int):
        '''
        The method checks whether a repository may be a source code repository.
        If it only contains a Readme file, a License file, and a .gitignore file,
        it is assumed that the repository is not a source code repository and
        can be rejected, therefore True is returned, as well as the number of
        remaining requests for the next API call.

        :param name: Repository name.
        :type name: str
        :param num_requests: Remaining requests, received from a preceding API call.
        :type num_requests: int
        :returns: flag indicating if repository may be a source code repository,
        number of remaining requests
        :rtype: (bool, int)
        '''
        raise NotImplementedError


    @abc.abstractmethod
    def get_first_commit(self, name: str, num_requests: int) -> (bool, str, str, int):
        '''
        The method requests the last commit and derives from the header the URL
        for the first commit to get its date. Returned are the flag of
        succesful request, the date of the first and last commit,
        as well as the number of remaining requestsf or the next API call.

        :param name: Repository name.
        :type name: str
        :param num_requests: Remaining requests.
        :type num_requests: int
        :returns: Succesful request flag, first commit date, last commit date,
        remaining rate limit or None
        :rtype: (bool, str, str, int)
        '''
        raise NotImplementedError
        