import json
import requests
from . import utils

API_HOST = 'https://webprod.plosjournals.org/api'

class Rhyno(object):
    def __init__(self, host=API_HOST, verify_ssl=False):
        self.host = host
        self.verify_ssl=verify_ssl

    '''EXCEPTIONS'''
    class Base405Error(Exception):
        def __init__(self, message):
            Exception.__init__(self, "Server responded with a 405: %s" % message)

    class Base404Error(Exception):
        def __init__(self, message):
            Exception.__init__(self, "Server responded with a 404: %s" % message)

    @staticmethod
    def handle_error_codes(r):
        if r.status_code == 405:
            raise Rhyno.Base405Error(r.content)
        if r.status_code == 404:
            raise Rhyno.Base404Error(r.content)

    def ingestible(self, verbose=False):
        '''
        returns list of ingestible DOIs as unicode
        '''
        r = requests.get(self.host + '/ingestible/', verify=self.verify_ssl)
        if verbose:
            print(utils.report("GET /ingestible/", r))
        return json.loads(r.content)

    def ingest(self, doi, force_reingest=None, verbose=False):
        '''
        attempts to ingest ingestible article by DOI
        returns article metadata dict if successful
        '''
        payload = {
            'doi': doi
            }
        if force_reingest:
            payload['force_reingest'] = True
        r = requests.post(self.host + '/ingestible', data=payload, verify=self.verify_ssl)
        if verbose:
            print(utils.report("POST /ingestible/ %s"% pretty_dict_repr(payload), r))

        self.handle_error_codes(r)
        return r.content

    def ingest_zip(self, archive_name, force_reingest=False, verbose=False):
        try:
            archive = open(archive_name, 'rb')
        except IOError as e:
            print(e)
            return -1
        files = {'archive': archive}
        payload = None
        if force_reingest:
            payload = {'force_reingest': True} 
        r = requests.post(self.host + '/zip/', files=files, data=payload, verify=self.verify_ssl)
        if verbose:
            print(utils.report("POST /zip/ %s"% utils.pretty_dict_repr(files), r))
        self.handle_error_codes(r)
        return json.loads(r.content)

    def get_metadata(self, doi, verbose=False):
        r = requests.get(self.host + '/article/' + doi, verify=self.verify_ssl)
        if verbose:
            print(utils.report("GET /ingestible/%s" % doi, r))
        self.handle_error_codes(r)        
        return json.loads(r.content)

    def _get_state(self, doi, verbose=False):
        r = requests.get(self.host + '/article/state/' + doi, verify=self.verify_ssl)
        if verbose:
            print(utils.report("GET /article/state/%s" % doi, r))
        self.handle_error_codes(r)
        return json.loads(r.content)
    
    def is_published(self, doi, verbose=False):
        return self._get_state(doi, verbose)['published']

    def get_crossref_syndication_state(self, doi, verbose=False):
        return self._get_state(doi, verbose)['crossRefSyndicationState']

    def get_pmc_syndication_state(self, doi, verbose=False):
        return self._get_state(doi, verbose)['pmcSyndicationState']

    def _base_publish(self, doi, publish, verbose=True):
        #'PENDING' has no effect on syndication
        payload = {
            'crossRefSynicationState': 'PENDING',
            'pmcSyndicationState': 'PENDING',
            'published': publish
            }
        r = requests.put(self.host + '/article/state/' + doi, data=json.dumps(payload), verify=self.verify_ssl)
        if verbose:
            print(utils.report("POST /article/state/" + doi, r))
        self.handle_error_codes(r) 
        return json.loads(r.content)

    def publish(self, doi, verbose=True):
        self._base_publish(doi, publish=True, verbose=verbose)

    def unpublish(self, doi, verbose=True):
        self._base_publish(doi, publish=False, verbose=verbose)

    def syndicate_pmc(self, doi, verbose=True):
        payload = {
            'crossRefSynicationState': 'PENDING',
            'pmcSyndicationState': 'IN_PROGRESS',
            'published': True
            }
        r = requests.put(self.host + '/article/state/' + doi, data=json.dumps(payload), verify=self.verify_ssl)
        if verbose:
            print(utils.report("POST /article/state/" + doi, r))
        self.handle_error_codes(r) 
        return json.loads(r.content)

    def syndicate_crossref(self, doi, verbose=True):
        payload = {
            'crossRefSynicationState': 'IN_PROGRESS',
            'pmcSyndicationState': 'PENDING',
            'published': True
            }
        r = requests.put(self.host + '/article/state/' + doi, data=json.dumps(payload), verify=self.verify_ssl)
        if verbose:
            print(utils.report("POST /article/state/" + doi, r))
        self.handle_error_codes(r) 
        return json.loads(r.content)
