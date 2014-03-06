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
        journals = self.r.get_journals()
        logger.debug(journals)

    def test_read_journals(self):
        plosone = self.r.read_journal('PLoSONE')
        logger.debug(plosone)


    def test_create_volume(self):
        new_volume = self.r.create_volume('PLoSONE', 'info:doi/10.1371/volume.pone.v10', #incr
                                          '2013', 'info:doi/10.1371/image.pbio.v01.i01',
                                          verbose=True)
        logger.debug(new_volume)

    def test_read_volume(self):
        logger.debug(self.r.get_volume('info:doi/10.1371/volume.pone.v01'))

    def test_create_issue(self):
        new_issue = self.r.create_issue('info:doi/10.1371/volume.pone.v01',
                                        'info:doi/10.1371/volume.pone.v01.i09', #incr
                                        '1', 'info:doi/10.1371/image.pbio.v01.i01',
                                        verbose=True)
        logger.debug(new_issue)

    def test_modify_issue(self):
        new_issue = self.r.modify_issue('info:doi/10.1371/volume.pone.v01.i01',
                                        '1', 'info:doi/10.1371/image.pbio.v01.i01',
                                        ['10.1371/journal.pone.0000001', '10.1371/journal.pone.0000000'])
        logger.debug(new_issue)


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
    
        
if __name__ == '__main__':
    unittest.main()
