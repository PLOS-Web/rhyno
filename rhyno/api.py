import json
import requests
from . import utils
import logging
logger = logging.getLogger(__name__)

API_HOST = 'https://webprod.plosjournals.org/api'

class Rhyno(object):
    def __init__(self, host=API_HOST, verify_ssl=False):
        self.host = host
        self.verify_ssl=verify_ssl

    '''EXCEPTIONS'''
    class Base400Error(Exception):
        def __init__(self, message):
            Exception.__init__(self, "Server responded with a 400: %s" % message)

    class Base405Error(Exception):
        def __init__(self, message):
            Exception.__init__(self, "Server responded with a 405: %s" % message)

    class Base404Error(Exception):
        def __init__(self, message):
            Exception.__init__(self, "Server responded with a 404: %s" % message)
            
    class Base500Error(Exception):
        def __init__(self, message):
            Exception.__init__(self, "Server responded with a 500: %s" % message)        

    @staticmethod
    def handle_error_codes(r):
        if r.status_code == 400:
            raise Rhyno.Base400Error(r.content)
        if r.status_code == 405:
            raise Rhyno.Base405Error(r.content)
        if r.status_code == 404:
            raise Rhyno.Base404Error(r.content)
        if r.status_code == 500:
            raise Rhyno.Base500Error(r.content)

    def ingestibles(self, verbose=False):
        '''
        returns list of ingestible DOIs as unicode
        '''
        r = requests.get(self.host + '/ingestibles/', verify=self.verify_ssl)
        if verbose:
            print(utils.report("GET /ingestibles/", r))
        return json.loads(r.content)

    def ingest(self, doi, force_reingest=None, verbose=False):
        '''
        attempts to ingest ingestible article by DOI
        returns article metadata dict if successful
        '''
        payload = {
            'name': doi
            }
        if force_reingest:
            payload['force_reingest'] = True
        r = requests.post(self.host + '/ingestibles', data=payload, verify=self.verify_ssl)
        if verbose:
            print(utils.report("POST /ingestibles/ %s" % pretty_dict_repr(payload), r))

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
        r = requests.get(self.host + '/articles/' + doi, verify=self.verify_ssl)
        if verbose:
            print(utils.report("GET /articles/%s" % doi, r))
        self.handle_error_codes(r)        
        return json.loads(r.content)

    def _get_state(self, doi, verbose=False):
        r = requests.get(self.host + '/articles/%s?state' % doi, verify=self.verify_ssl)
        if verbose:
            print(utils.report("GET /articles/%s?state" % doi, r))
        self.handle_error_codes(r)
        return json.loads(r.content)
    
    def is_published(self, doi, verbose=False):
        return self._get_state(doi, verbose)['state'] == 'published'

    def get_crossref_syndication_state(self, doi, verbose=False):
        return self._get_state(doi, verbose)['crossRefSyndicationState']

    def get_pmc_syndication_state(self, doi, verbose=False):
        return self._get_state(doi, verbose)['pmcSyndicationState']

    def _base_publish(self, doi, publish, verbose=False):
        #'PENDING' has no effect on syndication

        payload = {
            'state': 'published'
            }
        r = requests.patch(self.host + '/articles/%s' % doi, data=json.dumps(payload), verify=self.verify_ssl)
        if verbose:
            print(utils.report("PATCH /articles/%s" % doi, r))
        self.handle_error_codes(r) 
        return json.loads(r.content)

    def publish(self, doi, verbose=False):
        self._base_publish(doi, publish=True, verbose=verbose)

    def unpublish(self, doi, verbose=False):
        raise NotImplementedError
        self._base_publish(doi, publish=False, verbose=verbose)

    def syndicate_pmc(self, doi, verbose=False):
        raise NotImplementedError
        payload = {
            'crossRefSynicationState': 'PENDING',
            'pmcSyndicationState': 'IN_PROGRESS',
            'published': True
            }
        r = requests.put(self.host + '/articles/%s?state' % doi, data=json.dumps(payload), verify=self.verify_ssl)
        if verbose:
            print(utils.report("POST /articles/%s?state" % doi, r))
        self.handle_error_codes(r) 
        return json.loads(r.content)

    def syndicate_crossref(self, doi, verbose=False):
        raise NotImplementedError
        payload = {
            'crossRefSynicationState': 'IN_PROGRESS',
            'pmcSyndicationState': 'PENDING',
            'published': True
            }
        r = requests.put(self.host + '/articles/%s?state' % doi, data=json.dumps(payload), verify=self.verify_ssl)
        if verbose:
            print(utils.report("POST /articles/%s?state" % doi, r))
        self.handle_error_codes(r) 
        return json.loads(r.content)

    def get_journals(self, verbose=False):
        r = requests.get(self.host + "/journals", verify=self.verify_ssl)
        if verbose:
            print(utils.report("GET /journals", r))
        self.handle_error_codes(r)
        return json.loads(r.content)

    def read_journal(self, journal_key, verbose=False):
        r = requests.get(self.host + "/journals/%s" % journal_key, verify=self.verify_ssl)
        if verbose:
            print(utils.report("GET /journals/%s" % journal_key, r))
        self.handle_error_codes(r)
        return json.loads(r.content)

    def create_volume(self, journal_key, volume_uri, display_name, image_uri, verbose=False):
        payload = {
            'volumeUri': volume_uri,
            'displayName': display_name,
            'imageUri': image_uri,
        }
        r = requests.post(self.host + "/journals/%s" % journal_key, data=json.dumps(payload), verify=self.verify_ssl)
        if verbose:
            print(utils.report("POST /journals/%s" % journal_key, r))
        self.handle_error_codes(r)
        return r.content

    def get_volume(self, volume_uri, verbose=False):
        r = requests.get(self.host + "/volumes/%s" % volume_uri, verify=self.verify_ssl)
        if verbose:
            print(utils.report("GET /volume/%s" % volume_uri, r))
        self.handle_error_codes(r)
        return json.loads(r.content)

    def create_issue(self, volume_uri, issue_uri, display_name, image_uri, verbose=False):
        payload = {
            'issueUri': issue_uri,
            'displayName': display_name,
            'imageUri': image_uri,
            'respectOrder': True,
        }
        r = requests.post(self.host + "/volumes/%s" % volume_uri, data=json.dumps(payload), verify=self.verify_ssl)
        if verbose:
            print(utils.report("POST /volumes/%s" % volume_uri, r))
        self.handle_error_codes(r)
        return r.content

    def modify_issue(self, issue_uri, display_name, image_uri, article_order, verbose=False):
        payload = {
            'respectOrder': True,
            'issueUri': issue_uri,
            'displayName': display_name,
            'imageUri': image_uri,
            'articleOrder': article_order,
        }
        r = requests.patch(self.host + "/issues/%s" % issue_uri, data=json.dumps(payload), verify=self.verify_ssl)
        if verbose:
            print(utils.report("POST /issues/%s" % issue_uri, r))
        self.handle_error_codes(r)
        return r.content
