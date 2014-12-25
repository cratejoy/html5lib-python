import html5lib
import unittest
import logging

log = logging.getLogger(__name__)


def dump(tree, tabs=0):
    log.debug(u"{}Tag '{}' - {} children - Value = {}".format(
        "".join(["\t" for i in range(tabs)]), tree.tag, len(tree), tree.attrib['value'] if 'value' in tree.attrib else None))

    for child in tree:
        dump(child, tabs + 1)


class JinjaTestCase(unittest.TestCase):
    def test_var_1(self):
        parser = html5lib.HTMLParser(strict=False)

        html_string = """<h1>{{ hi }}</h1>"""

        tree = parser.parseFragment(html_string)

        h1 = tree[0]
        self.assertEqual(h1.tag, "{http://www.w3.org/1999/xhtml}h1")

    def test_filter_1(self):
        parser = html5lib.HTMLParser(strict=False)

        html_string = """<h1>{{ hi | yo }}</h1>"""

        tree = parser.parseFragment(html_string)

        h1 = tree[0]
        self.assertEqual(h1.tag, "{http://www.w3.org/1999/xhtml}h1")

        jt = h1[0]

        hi = jt[0]
        pipe1 = jt[1]
        yo = jt[2]

        self.assertEqual(hi.tag, 'jinjavariable')
        self.assertEqual(hi.attrib['value'], 'hi')
        self.assertEqual(pipe1.tag, 'jinjapipe')
        self.assertEqual(pipe1.attrib['value'], '|')
        self.assertEqual(yo.tag, 'jinjafilter')
        self.assertEqual(yo.attrib['value'], 'yo')

    def test_filter_2(self):
        parser = html5lib.HTMLParser(strict=False)

        html_string = """<h1>{{ hi | yo("hi") }}</h1>"""

        tree = parser.parseFragment(html_string)
        dump(tree)

        h1 = tree[0]
        self.assertEqual(h1.tag, "{http://www.w3.org/1999/xhtml}h1")

        jt = h1[0]

        hi = jt[0]
        pipe1 = jt[1]
        yo = jt[2]

        self.assertEqual(hi.tag, 'jinjavariable')
        self.assertEqual(hi.attrib['value'], 'hi')
        self.assertEqual(pipe1.tag, 'jinjapipe')
        self.assertEqual(pipe1.attrib['value'], '|')
        self.assertEqual(yo.tag, 'jinjafilter')
        self.assertEqual(yo.attrib['value'], 'yo')

        arg1 = yo[0]

        self.assertEqual(arg1.tag, 'jinjaargument')
        self.assertEqual(arg1.attrib['value'], '"hi"')
