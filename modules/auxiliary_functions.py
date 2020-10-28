''' auxiliary functions '''

import re


def extract_doi(fragment):
    '''
    The function searches in the given string valid DOI names. A DOI name
    is case insensitive. To avoid duplicates all uppercase letters converted
    to lowercase letters.

    :param fragment: string to lookup DOI names and short DOI names.
    :type fragment: str.
    :returns: list of found DOIs.
    :rtype: [str].
    :raises: AttributeError, KeyError
    '''

    ignored_suffixes = ['.pdf', '.svg']
    dois = []
    # extract the DOI reference from the description and Readme file
    # new general pattern that allows blanks before and after the forward slash
    general_pattern = r'(10 ?\. ?[0-9]{4,}(?:[.][0-9]+)* ?/ ?[-._;()/:A-Za-z0-9]+)'
    short_pattern = r'((?:doi\.org| 10|doi\.org/10|doi ?: ?10)/(?!10)[a-zA-Z0-9]+)[`\s><.)]'

    list_of_dois = re.findall(general_pattern, fragment)
    # some doi names are part of a pdf link and have a not required extension, which is cleared
    for doi in list_of_dois:
        doi = doi.lower()
        appended = False
        for suffix in ignored_suffixes:
            if doi.endswith(suffix):
                dois.append(doi[:-len(suffix)])
                appended = True
        if not appended:
            dois.append(doi)
    list_of_dois = re.findall(short_pattern, fragment)
    for doi in list_of_dois:
        doi = doi.lower()
        dois.append('10/' + doi.rsplit('/', 1)[1])
    return dois


def create_reference_entry(publication, include_doi):
    '''
    Checks the given identifier of a publication and
    return an entry for the rsPublications database table
    and the repositories references list.

    :param publication: Publication entry.
    :type publication: dict
    :returns: Reference entry for database tables.
    :rtype: dict
    '''

    if 'doi' in publication and publication['doi'] and include_doi:
        return {'id' : publication['doi'], 'mode': 'doi'}
    if 'doi_from_link' in publication and publication['doi_from_link'] and include_doi:
        return {'id' : publication['doi_from_link'], 'mode': 'doi'}
    if 'arxiv_id' in publication and publication['arxiv_id']:
        return {'id' : publication['arxiv_id'], 'mode': 'arxiv_id'}
    if 'title' in publication and publication['title']:
        return {'id' : publication['title'], 'mode': 'title'}
    return None


def check_name_suffix(name):
    '''
    Some extracted repository and DOI names end with a full stop,
    a closing parathesis, .git, or .The. These suffixes are
    removed and the shortned name is returned. In the case that
    an entry for the truncated name in the database table exists,
    or the name may not be shortened, None is returned.

    :param database: Database table name.
    :type database: MongoDB database
    :param name: Repository or DOI name.
    :type name: string
    :param mode: Repository or publication.
    :type mode: str
    :returns: Truncated repository name.
    :rtype: string or None
    '''

    ignored_suffixes = ['.git', '.The', 'pdf', '.svg', '.In', 'fulltext', 'meta',
                        '.html', 'abstract', '.To', 'full', 'status', 'epdf', 'full',
                        'jsessionid', 'users', 'badges', 'issuetoc', 'suppinfo']

    for suffix in ignored_suffixes:
        if name.endswith(suffix):
            return name[:-len(suffix)]

    if not name[-1].isalnum():
        return name[:-1]

    return None
