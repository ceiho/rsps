''' ArXivHarvester '''

import time
from datetime import datetime
import requests
import feedparser
from interfaces.publication_harvester import PublicationHarvester


class ArXivHarvester(PublicationHarvester):
    '''
    .. class:: ArXivHarvester

    The ArXivHarvester class contains all mandatory methods to gather research
    publications containing a github.com link.  In the summary, summary_detail
    and arxiv_comments repository full names and repository owners are looked up
    with regular expressions. The retrieved list of names is stored together with
    other collected date in one database table entry for each publication. To comply
    with the request to sleep a bit before calling the API, recommended are three
    seconds, the sleep time between two API calls is set to 5 seconds.


    :param start: specify the number of the first publivation to be returned.
    :type start: int
    :param results_per_iteraton: number of publications returned.
    :type results_per_iteration: int
    :param wait_time: sleeping time between two API calls.
    :type wait_time: int
    '''

    # base arXiv API url
    BASE_URL = 'http://export.arxiv.org/api/query?search_query=all:'

    def __init__(self, start=0, results_per_iteration=1000, wait_time=5):
        '''
        Constructor method
        '''

        self.start = start
        self.results_per_iteration = results_per_iteration
        self.wait_time = wait_time


    def harvest(self, query, db_collection):
        """
        This procedure harvests publications on arXiv containing a specified search
        term using the provided API.
        When using the legacy APIs (including OAI-PMH, RSS, and the arXiv API),
        make no more than one request every three seconds, and limit requests to a
        single connection at a time. (https://arxiv.org/help/api/tou)
        maximum number of results returned from a single call (max_results) is limited
        to 30000 in slices of at most 2000 at a time, using the max_results and
        start (https://arxiv.org/help/api/user-manual)

        This code is based on the examples:
            https://static.arxiv.org/static/arxiv.marxdown/0.1/help/api/examples/python_arXiv_paging_example.txt
            https://static.arxiv.org/static/arxiv.marxdown/0.1/help/api/examples/python_arXiv_parsing_example.txt

        :param query: search term.
        :type query: str
        :param db_collection: Database table name to store the publications in.
        :type db_collection: MongoDB collection instance
        """

        # get max num results
        response = requests.get(
            self.BASE_URL+query+'&start=0&max_results=1')
        feed = feedparser.parse(response.text)
        total_results = int(feed.feed.opensearch_totalresults)
        time.sleep(self.wait_time)
        print("Number of total results: ", total_results)

        for i in range(self.start, total_results, self.results_per_iteration):
            print("Results %i - %i" % (i, i+self.results_per_iteration))
            current_query = '%s&start=%i&max_results=%i' % (query,
                                                            i,
                                                            self.results_per_iteration)
            response = requests.get(self.BASE_URL+current_query)

            feed = feedparser.parse(response.text)

            # Iterate over the returned entries
            for entry in feed.entries:
                link = ''
                pdf_url = ''
                doi_url = ''
                doi = ''

                ident = entry.id.rsplit('arxiv.org/abs/', 1)[1]

                # get the links to the abs page and pdf for this e-print
                for link in entry.links:
                    if link.rel == 'alternate':
                        link = link.href
                    elif link.title == 'pdf':
                        pdf_url = link.href
                    elif link.title == 'doi':
                        doi_url = link.href
                        doi = doi_url.rsplit('doi.org/', 1)[1]

                # get the journal reference
                try:
                    journal_ref = entry.arxiv_journal_ref
                except AttributeError:
                    journal_ref = 'No journal ref found'

                # get the primary category of the entry
                primary_category = entry.tags[0]['term']

                # get all categories of the entry
                all_cat = [t['term'] for t in entry.tags]
                all_categories = (', ').join(all_cat)

                # get the summary, summary_detail
                summary = entry.summary if hasattr(entry,'summary') else ''
                sum_detail = entry.summary_detail['value'] if hasattr(entry,
                                                                      'summary_detail') else ''
                comment = entry.arxiv_comment if hasattr(entry, 'arxiv_comment') else ''

                # store metadata of each publication in db
                post = {"source": "arxiv",
                        "request_date": datetime.now(),
                        "arxiv_id": ident,
                        "doi": doi,
                        "title": entry.title,
                        "published": entry.published,
                        "updated": entry.updated,
                        "url": entry.id,
                        "DOI_url": doi_url,
                        "pdf_url": pdf_url,
                        "primary_category": primary_category,
                        "all_categories": all_categories,
                        "journal_ref": journal_ref,
                        "total_citations": None,
                        "total_downloads": None,
                        "summary": summary,
                        "summary_detail": sum_detail,
                        "arxiv_comment": comment
                        }
                db_collection.save(post)

            time.sleep(self.wait_time)
