''' Interface for publications harvester classes '''

import abc

class PublicationHarvester(metaclass=abc.ABCMeta):
    '''

    .. class:: PublicationHarvester

    Defines the signature operations for publication harvester classes.
    '''

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'harvest') and
                callable(subclass.harvest) or
                NotImplemented)


    @abc.abstractmethod
    def harvest(self, query: str, db_collection: str) -> None:
        '''
        This procedure harvests publications containing a
        specified search term using the provided API

        :param query: search term.
        :type query: str
        :param db_collection: Database table name to store the publications in.
        :type db_collection: MongoDB collection instance
        :returns: None
        :rtype: None
        '''
        raise NotImplementedError
