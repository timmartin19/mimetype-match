from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest2

from accept_header_match import _is_more_specific, MimeType, AcceptHeader, InvalidMimeType,\
    get_best_match


class TestAccept(unittest2.TestCase):
    def test_is_more_specific(self):
        self.assertFalse(_is_more_specific('*/*', 'text/*'))
        self.assertFalse(_is_more_specific('*/*', '*/text'))
        self.assertFalse(_is_more_specific('text/*', 'text/something'))
        self.assertFalse(_is_more_specific('text/*', 'html/something'))

        self.assertTrue(_is_more_specific('text/*', '*/*'))
        self.assertTrue(_is_more_specific('*/text', '*/*'))
        self.assertTrue(_is_more_specific('text/something', 'text/*'))
        self.assertTrue(_is_more_specific('html/something', 'text/*'))

        self.assertIsNone(_is_more_specific('*/*', '*/*'))
        self.assertIsNone(_is_more_specific('text/*', 'html/*'))
        self.assertIsNone(_is_more_specific('*/text', '*/html'))

    def test_content_type_weight(self):
        mimes = ['text/*;q=0.3', 'text/html;level=1', 'text/html;level=2;q=0.4', '*/*;q=0.5']
        expected = [0.3, 1.0, 0.4, 0.5]
        for mime, expc in zip(mimes, expected):
            ct = MimeType(mime)
            self.assertEqual(ct.weight, expc)

    def test_content_type(self):
        mimes = ['text/*;q=0.3', 'text/html;level=1', 'text/html;level=2;q=0.4', '*/*;q=0.5']
        expected = ['text/*', 'text/html;level=1', 'text/html;level=2', '*/*']
        for mime, expc in zip(mimes, expected):
            ct = MimeType(mime)
            self.assertEqual(ct.mimetype, expc)

    def test_content_type_eq(self):
        ct = MimeType('text/*;')
        self.assertFalse(ct == None)
        self.assertFalse(ct == MimeType('text/*;q=0.5'))
        self.assertTrue(ct == MimeType('text/*;q=1'))

    def test_content_type_gt(self):
        ct = MimeType('text/*;q=0.7')
        self.assertTrue(ct > None)
        self.assertTrue(ct > MimeType('text/*;q=0.5'))
        self.assertFalse(ct > MimeType('text/*;q=1'))
        self.assertFalse(ct > MimeType('text/*;q=0.7'))

    def test_content_type_lt(self):
        ct = MimeType('text/*;q=0.7')
        self.assertFalse(ct < None)
        self.assertFalse(ct < MimeType('text/*;q=0.5'))
        self.assertTrue(ct < MimeType('text/*;q=1'))
        self.assertFalse(ct < MimeType('text/*;q=0.7'))

    def test_content_type_ge(self):
        ct = MimeType('text/*;q=0.7')
        self.assertTrue(ct >= None)
        self.assertTrue(ct >= MimeType('text/*;q=0.5'))
        self.assertFalse(ct >= MimeType('text/something;q=0.5'))
        self.assertTrue(ct >= MimeType('*/*;q=0.5'))
        self.assertFalse(ct >= MimeType('text/*;q=1'))
        self.assertTrue(ct >= MimeType('text/*;q=0.7'))

    def test_content_type_le(self):
        ct = MimeType('text/*;q=0.7')
        self.assertFalse(ct <= None)
        self.assertFalse(ct <= MimeType('text/*;q=0.5'))
        self.assertTrue(ct <= MimeType('text/something;q=0.5'))
        self.assertFalse(ct <= MimeType('*/*;q=0.5'))
        self.assertTrue(ct <= MimeType('text/*;q=1'))
        self.assertTrue(ct <= MimeType('text/*;q=0.7'))

    def test_accept_headers_order(self):
        value = ('text/*;q=0.3, text/html;q=0.7, text/html;level=1,'
                 'text/html;level=2;q=0.4, */*;q=0.5')
        accept_header = AcceptHeader(value)
        content_types = [ct.mimetype for ct in accept_header]
        self.assertListEqual(['text/html;level=1', 'text/html',
                              'text/html;level=2', 'text/*', '*/*'], content_types)

    def test_accept_headers_get_match(self):
        value = ('text/*;q=0.3, text/html;q=0.7, text/html;level=1,'
                 'text/html;level=2;q=0.4, */*;q=0.5')
        accept_header = AcceptHeader(value)
        best = accept_header.get_match('text/something')
        self.assertEqual(best.mimetype, 'text/*')
        best = accept_header.get_match('text/html')
        self.assertEqual(best.mimetype, 'text/html')
        best = accept_header.get_match('*/*')
        self.assertEqual(best.mimetype, '*/*')
        best = accept_header.get_match('blah/*')
        self.assertEqual(best.mimetype, '*/*')

    def test_accept_headers_get_best_match(self):
        value = ('text/*;q=0.3, text/html;q=0.7, text/html;level=1,'
                 'text/html;level=2;q=0.4, */*;q=0.5')
        accept_header = AcceptHeader(value)
        best = accept_header.get_best_match(['text/json', 'blah/blah'])
        self.assertEqual(best[0].mimetype, 'text/*')
        self.assertEqual(best[1], 'text/json')

    def test_invalid_accept_header(self):
        self.assertRaises(InvalidMimeType, MimeType, '')
        self.assertRaises(InvalidMimeType, MimeType, ';  ; ;;')
        self.assertRaises(InvalidMimeType, MimeType, 'somofmdfog')
        self.assertRaises(InvalidMimeType, MimeType, 'text/html;q=blah')

    def test_accept_headers_get_match_none(self):
        value = ('text/*;q=0.3, text/html;q=0.7, text/html;level=1,'
                 'text/html;level=2;q=0.4')
        accept_header = AcceptHeader(value)
        self.assertIsNone(accept_header.get_match('application/json'))

    def test_accept_headers_get_best_match_none(self):
        value = ('text/*;q=0.3, text/html;q=0.7, text/html;level=1,'
                 'text/html;level=2;q=0.4')
        accept_header = AcceptHeader(value)
        self.assertIsNone(accept_header.get_best_match('application/json'))

    def test_accept_headers_no_headers(self):
        self.assertListEqual([], AcceptHeader(', ,,  , , ').mimetypes)

    def test_get_best_match(self):
        best = get_best_match(('text/*;q=0.3, text/html;q=0.7, text/html;level=1,'
                               'text/html;level=2;q=0.4, */*;q=0.5'),
                              ['text/json', 'blah/blah'])
        self.assertEqual(best[0].mimetype, 'text/*')
        self.assertEqual(best[1], 'text/json')

    def test_get_best_match_list(self):
        best = get_best_match([
            'text/*;q=0.3', 'text/html;q=0.7', 'text/html;level=1',
            'text/html;level=2;q=0.4', '*/*;q=0.5'],
            ['text/json', 'blah/blah'])
        self.assertEqual(best[0].mimetype, 'text/*')
        self.assertEqual(best[1], 'text/json')
