from __future__ import absolute_import

import unittest
import logging
logger = logging.getLogger(__name__)

from ..api import Rhyno

API_HOST = 'https://webprod.plosjournals.org/api'
SHELL_HOST = 'iad-webprod-devstack01.int.plos.org'
TEST_PACKAGE_FILENAME = 'pone.0057000.zip'
TEST_PACKAGE_DOI = 'info:doi/10.1371/journal.pone.0057000'
DOI_PREFIX = "info:doi/10.1371/journal."

class TestVolIss(unittest.TestCase):
    def setUp(self):
        self.r = Rhyno(API_HOST)

    def test_get_journals(self):
        logger.debug("testing get journals ...")
        journals = self.r.get_journals()
        logger.debug(journals)





class TestRhinoAPI(unittest.TestCase):
    def setUp(self):     
        self.r = Rhyno(API_HOST)
    
    def test_ingestibles_get(self):
        ret = self.r.ingestibles(verbose=True)

    def test_ingest_zip(self):
        with self.assertRaises(Rhyno.Base405Error):
            self.r.ingest_zip(TEST_PACKAGE_FILENAME, verbose=True)
        #self.r.ingest_zip(TEST_PACKAGE_FILENAME, force_reingest=True, verbose=True)

    def test_get_article(self):
        self.r.get_metadata(TEST_PACKAGE_DOI, verbose=True)

    def test_get_article_state(self):
        self.r._get_state(TEST_PACKAGE_DOI, verbose=True)

    def test_publish(self):
        self.r.publish(TEST_PACKAGE_DOI, verbose=True)
        self.assertTrue(self.r.is_published(TEST_PACKAGE_DOI))

    def test_unpublish(self):
        self.r.unpublish(TEST_PACKAGE_DOI, verbose=True)
        self.assertFalse(self.r.is_published(TEST_PACKAGE_DOI))

    def test_pmc_syndication_state(self):
        self.r.get_pmc_syndication_state(TEST_PACKAGE_DOI, verbose=True)

    def test_crossref_syndication_state(self):
        self.r.get_crossref_syndication_state(TEST_PACKAGE_DOI, verbose=True)

    def test_syndicate_pmc(self):
        self.r.syndicate_pmc(TEST_PACKAGE_DOI, verbose=True)

    def test_syndicate_crossref(self):
        self.r.syndicate_crossref(TEST_PACKAGE_DOI, verbose=True)
    
        
if __name__ == '__main__':
    unittest.main()
