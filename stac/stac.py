#
# This file is part of Python Client Library for STAC.
# Copyright (C) 2019 INPE.
#
# Python Client Library for STAC is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Python API client wrapper for STAC."""
import warnings

from requests import HTTPError

from .catalog import Catalog
from .collection import Collection
from .item import ItemCollection
from .utils import Utils


class STAC:
    """This class implements a Python API client wrapper for STAC.

    See https://github.com/radiantearth/stac-spec for more information on STAC.

    :param url: The STAC server URL.
    :type url: str
    """

    def __init__(self, url, validate=False, access_token=None):
        """Create a STAC client attached to the given host address (an URL)."""
        self._url = url if url[-1] != '/' else url[0:-1]
        self._collections = dict()
        self._catalog = dict()
        self._validate = validate
        self._access_token = f'?access_token={access_token}' if access_token else ''

    @property
    def conformance(self): # pragma: no cover
        """Return the list of conformance classes that the server conforms to."""
        return Utils._get('{}/conformance'.format(self._url))

    @property
    def catalog(self):
        """
        Retrieve the available collections in the STAC Catalog.

        :return list of available collections.
        """
        if len(self._collections) > 0:
            return list(self._collections.keys())

        url = f'{self._url}/stac{self._access_token}'
        self._catalog = Catalog(Utils._get(url), self._validate)

        for i in self._catalog.links:
            if i.rel == 'child':
                if '?' in i.href:
                    collection_name = i.href.split('/')[-1]
                    self._collections[collection_name[:collection_name.index('?')]] = None
                else:
                    self._collections[i.href.split('/')[-1]] = None
        return list(self._collections.keys())

    def collection(self, collection_id):
        """Return the given collection.

        :param collection_id: A str for a given collection_id.
        :type collection_id: str

        :returns: A STAC Collection.
        :rtype: dict
        """

        if collection_id in self._collections.keys() and \
            self._collections[collection_id] is not None:
            return self._collections[collection_id]
        try:
            data = Utils._get(f'{self._url}/collections/{collection_id}{self._access_token}')
            self._collections[collection_id] = Collection(data, self._validate)
        except HTTPError as e:
            raise KeyError(f'Could not retrieve information for collection: {collection_id}')
        return self._collections[collection_id]


    def search(self, filter=None):
        """Retrieve Items matching a filter.

        :param filter: (optional) A dictionary with valid STAC query parameters.
        :type filter: dict

        :returns: A GeoJSON FeatureCollection.
        :rtype: dict
        """
        url = f'{self._url}/stac/search{self._access_token}'
        data = Utils._get(url, params=filter)
        return ItemCollection(data, self._validate)

    @property
    def url(self):
        """Return the STAC server instance URL."""
        return self._url

    def __repr__(self):
        """Return the string representation of a STAC object."""
        text = 'stac("{}")'.format(self.url)
        return text

    def __str__(self):
        """Return the string representation of a STAC object."""
        return '<STAC [{}]>'.format(self.url)
