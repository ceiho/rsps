'''
Database class
'''

import subprocess
from io import BytesIO
from urllib.request import urlopen
from zipfile import ZipFile
from os import path
import json
from pymongo import MongoClient
import yaml


class _Database():
    '''

    .. class:: Database

    The Database class contains all mandatory methods to
    interact with MongoDB. As no instances of different
    database are created, it is not initialized.
    '''

    DATABASE = None
    DATABASE_NAME = None

    @staticmethod
    def initialize(name):
        '''
        The method initializes the connection to MongoDB and
        checks whether the specified database tables exist.
        '''
        _Database.DATABASE_NAME = name
        _Database.DATABASE = getattr(MongoClient(), name)


    @staticmethod
    def insert_one(collection, data):
        '''
        Adds the data to the specified database collection.

        :param collection: Database collection.
        :type collection: pymongo.collection.Collection
        :param data: Data to be added.
        :type data: dict
        :returns: Result message.
        :rtype: pymongo.results.InsertOneResult
        '''
        _Database.DATABASE[collection].insert_one(data)


    @staticmethod
    def count_documents(collection, query):
        '''
        Returns the number of documents in the database table
        with the specified characteristics.

        :param collection: Database collection.
        :type collection: pymongo.collection.Collection
        :param query: Characteristics to be met by the documents to be counted.
        :type query: dict
        :returns: Number of documents meeting the characteristics.
        :rtype: int
        '''
        return _Database.DATABASE[collection].count_documents(query)


    @staticmethod
    def find(collection, query):
        '''
        Returns the documents from the database table
        with the specified characteristics.

        :param collection: Database collection.
        :type collection: pymongo.collection.Collection
        :param query: Characteristics to be met by the documents.
        :type query: dict
        :returns: Documents meeting the characteristics.
        :rtype: pymongo.cursor.Cursor
        '''
        return _Database.DATABASE[collection].find(query)


    @staticmethod
    def find_with_batch_size(collection, query, size):
        '''
        Returns the documents from the database table
        with the specified characteristics.

        :param collection: Database collection.
        :type collection: pymongo.collection.Collection
        :param query: Characteristics to be met by the documents.
        :type query: dict
        :param size: Batch size.
        :type size: int
        :returns: Documents meeting the characteristics.
        :rtype: pymongo.cursor.Cursor
        '''
        return _Database.DATABASE[collection].find(query, batch_size=size)


    @staticmethod
    def aggregate(collection, features):
        '''
        Returns the documents matching the features.

        :param collection: Database collection.
        :type collection: pymongo.collection.Collection
        :param queries: Characteristics to be met by the documents.
        :type queries: [dict]
        :returns: Sorted documents matching the characteristics.
        :rtype: pymongo.cursor.Cursor
        '''
        return _Database.DATABASE[collection].aggregate(features)


    @staticmethod
    def find_one(collection, query):
        '''
        Returns one document from the database table
        with the specified characteristics.

        :param collection: Database collection.
        :type collection: pymongo.collection.Collection
        :param query: Characteristics to be met by the document.
        :type query: dict
        :returns: Document meeting the characteristics.
        :rtype: pymongo.cursor.Cursor
        '''
        return _Database.DATABASE[collection].find_one(query)


    @staticmethod
    def update_one(collection, ident, query):
        '''
        Modifies the document in the database table
        with the specified query.

        :param collection: Database collection.
        :type collection: pymongo.collection.Collection
        :param ident: Document to be modified.
        :type ident: dict
        :param query: Fields to be updated.
        :type query: dict
        :returns: Result message.
        :rtype: pymongo.results.UpdateResult
        '''
        _Database.DATABASE[collection].update_one(ident, query)


    @staticmethod
    def delete_one(collection, query):
        '''
        Deletes one document from the database table
        with the specified characteristics.

        :param collection: Database collection.
        :type collection: pymongo.collection.Collection
        :param query: Characteristics to be met by the document.
        :type query: dict
        :returns: Result message.
        :rtype: pymongo.results.DeleteResult
        '''
        _Database.DATABASE[collection].delete_one(query)



class Collection():
    '''

    .. class:: Collection

    The Collection class provides all mandatory methods for the
    data handling in database tables.

    :param mode: Intended purpose of the database collection.
    :type mode: str
    '''


    @staticmethod
    def _check_db_collection_name(name, mode, data_url=None):
        '''
        The function checks whether the passed database table already
        exists.

        :param name: Database table name.
        :type name: str
        :param mode: Intended use of database table.
        :type mode: str
        :param data_url: URL to load existing database files in bson format.
        :type data_url: str
        :returns: Name of current database table.
        :rtype: str
        '''

        if (not _Database.DATABASE.list_collection_names()
            and not path.exists('data')
            and data_url
           ):
            try:
                with urlopen(data_url) as zipresp:
                    with ZipFile(BytesIO(zipresp.read())) as zfile:
                        print('Extracting zip file ...')
                        zfile.extractall('data')
            except:
                print('Something went wrong. Database files are not loaded.')

        if ((not _Database.DATABASE.list_collection_names()
             or not name in _Database.DATABASE.list_collection_names())
            and path.exists('data/' + name + '.bson')):
            cmd = ('mongorestore -d ' + _Database.DATABASE_NAME
                   + ' -c ' + name + ' data/' + name + '.bson')
            print('Restoring database table ' + name + ' ...')
            try:
                subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
            except subprocess.CalledProcessError as error_message:
                if error_message.output.startswith('error: {'):
                    error = json.loads(error_message.output[7:])
                    print(error['code'] + ': ' + error['message'])
                else:
                    print(error_message.output)

        if (_Database.DATABASE.list_collection_names()
            and not name in _Database.DATABASE.list_collection_names()):
            print('Database table', name,
                  'is not available. Confirm or specify another database table name:')
            name = input()
        if mode in ['arxiv_subjects', 'publication_subjects']:
            while not name in _Database.DATABASE.list_collection_names():
                print('The database table is required to determine the repository subject,',
                      'but the specified one is not available. Define the correct name:')
                name = input()
        return name


    def __init__(self, mode):
        '''
        Constructor
        '''

        with open("config.yaml", 'r') as stream:
            try:
                params = (yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)

        if _Database.DATABASE != params['database']['name']:
            _Database.initialize(params['database']['name'])

        self.collection_name = Collection._check_db_collection_name(
            params['database']['collections'][mode],
            mode,
            params['database']['data_url']
        )


    def save(self, query):
        '''
        Inserts the passed information.

        :param query: Parameter to be inserted.
        :type query: dict
        :returns: None.
        :rtype: None
        '''
        _Database.insert_one(self.collection_name, query)


    def get_number_of_entries(self, query):
        '''
        Returns the number of entries from the database table
        with the specified characteristics.

        :param query: Characteristics to be met by the entries.
        :type query: dict
        :returns: Number of entries meeting the characteristics.
        :rtype: int
        '''
        return _Database.count_documents(self.collection_name, query)


    def get_entries(self, query):
        '''
        Returns the entries from the database table
        with the specified characteristics.

        :param query: Characteristics to be met by the entries.
        :type query: dict
        :returns: Entries meeting the characteristics.
        :rtype: pymongo.cursor.Cursor
        '''
        return _Database.find_with_batch_size(self.collection_name, query, 50)


    def get_entry(self, query):
        '''
        Returns the entry from the database table
        with the specified characteristics.

        :param query: Characteristics to be met by the entry.
        :type query: dict
        :returns: Entry meeting the characteristics.
        :rtype: pymongo.cursor.Cursor
        '''
        return _Database.find_one(self.collection_name, query)


    def mod_entry(self, ident, query):
        '''
        Modifies the specified entry with the specified parameters.

        :param ident: Entry to be modified.
        :type ident: dict
        :param query: Parameters to be modified.
        :type query: dict
        :returns: None.
        :rtype: None
        '''
        _Database.update_one(self.collection_name, ident, query)


    def remove_entry(self, query):
        '''
        Removes the specified entry from the database table.

        :param query: Entry to be deleted.
        :type query: dict
        :returns: None.
        :rtype: None
        '''
        _Database.delete_one(self.collection_name, query)



class RepoCollection(Collection):
    '''

    .. class:: RepoCollection

    The RepoCollection class provides additional methods to handle
    the harvested repositories.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__('repositories')


    def save_repo(self, elem, key, source, date):
        '''
        Adds the harvested repository metadata.

        :param elem: Repository metadata.
        :type elem: dict
        :param key: Search term found in repository.
        :type key: str
        :param source: Hosting service of the repository.
        :type source: str
        :param date: Harvesting date.
        :type date: datetime.datetime
        :returns: None.
        :rtype: None
        '''
        if self.get_entry({'id': elem['id']}):
            self.mod_entry({'id': elem['id']},
                            {'$addToSet': {'keywords': key}})
        else:
            elem['source'] = source
            elem['keywords'] = [key]
            elem['request_date'] = date
            self.save(elem)



class RsRepoCollection(Collection):
    '''

    .. class:: RsRepoCollection

    The RsRepoCollection class provides additional methods to handle
    the research software repositories.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__('rs_repositories')


    def save_repo(self, id_num, name, ids, source, group, language=None):
        '''
        Depending on an existend entry for a research software repository,
        the information are added to the entry, or a new entry is inserted.

        :param id_num: Repository ID.
        :type id_num: int
        :param name: Repository full name.
        :type name: str
        :param ids: list of IDs.
        :type ids: [dict]
        :param source: Hosting service of the repository.
        :type source: str
        :param group: Evaluation group of the repository.
        :type group: str
        :param language: Repository primary language.
        :type language: str
        :returns: None.
        :rtype: None
        '''

        query = {'id': id_num} if id_num else {'full_name': name}
        if self.get_entry(query):
            for ident in ids:
                self.mod_entry(
                    query,
                    {'$addToSet': {'references': ident,
                                   'group': group}})
        else:
            self.save(
                {'id': id_num,
                 'full_name': name,
                 'group': [group],
                 'source': source,
                 'language': language,
                 'references': ids})


    def save_subject(self, name, subject):
        '''
        The function updates a repository entry with the disciplines,
        if the fields already exists the values are appended.

        :param name: Repository to be updated.
        :type name: str
        :param subject: Main disciplineSubject information.
        :type main: str
        :return: None.
        :rtype: None
        '''

        mode = 'addToSet' if 'main_subject' in self.get_entry({'_id': name}) else 'set'
        genus = subject['subgroups'] if 'subgroups' in subject else [None]

        if mode == 'set':
            self.mod_entry(
                {'_id':name},
                {'$set': {'main_subject': subject['supergroup'],
                          'subject': subject['groups'],
                          'sub_subject': genus}})
        elif mode == 'addToSet':
            for elem in subject['supergroup']:
                self.mod_entry(
                    {'_id':name},
                    {'$addToSet': {'main_subject': elem}})
            for elem in subject['groups']:
                self.mod_entry(
                    {'_id':name},
                    {'$addToSet': {'subject': elem}})
            for elem in genus:
                self.mod_entry(
                    {'_id':name},
                    {'$addToSet': {'sub_subject': elem}})
        else:
            pass


    def update_doi(self, repo_id, doi, ident=None):
        '''
        An unidentifiable DOI is removed in the references
        of the repositories. If an alternative identifier
        (arxiv_id or title) is available, the repository is
        updated.

        :param repo_id: Research software repository to be modified.
        :type repo_id: str
        :param doi: unidentifiable DOI name.
        :type doi: str
        :param ident: Alternative publication identifier.
        :type ident: dict | None.
        :returns: None.
        :rtype: None
        '''

        self.mod_entry({'_id':repo_id},
                       {'$pull':
                        {'references':
                         {'id':doi, 'mode':'doi'}}})
        if ident:
            self.mod_entry(
                {'_id': repo_id},
                {'$addToSet':
                 {'references': ident}})



class RsPublicationCollection(Collection):
    '''

    .. class RsPublicationCollection

    The RsPublicationCollection class provides additional
    methods to handle the harvested research software
    publications.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__('rs_publications')


    def save_publication(self, ids, repo):
        '''
        Depending on an existend entry for a publication, the information
        are added to the entry, or a new entry is inserted.
        Look up the publication id in the database table,
        if exists, update its repository name list
        else create a new entry for the publication with its repository.

        :param ids: list of IDs.
        :type ids: [dict]
        :param repo: Repository name.
        :type repo: str
        '''

        for ident in ids:
            if self.get_entry({'identifier.id': ident['id']}):
                self.mod_entry(
                    {'identifier.id': ident['id']},
                    {'$addToSet': {'repos': repo}})
            else:
                self.save(
                    {'identifier': ident,
                     'repos': [repo]})
