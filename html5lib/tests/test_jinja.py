import html5lib
import unittest
import logging

log = logging.getLogger(__name__)


def dump(tree, tabs=0):
    log.debug(u"{}Tag '{}' - {} children - Value = {} - Text = {}".format(
        "".join(["\t" for i in range(tabs)]), tree.tag, len(tree), tree.attrib['value'] if 'value' in tree.attrib else None, tree.text))

    for child in tree:
        dump(child, tabs + 1)


class JinjaTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = html5lib.HTMLParser(strict=False, namespaceHTMLElements=False)

    def test_var_1(self):
        html_string = """<h1>{{ hi }}</h1>"""

        tree = self.parser.parseFragment(html_string)

        h1 = tree[0]
        jt = h1[0]
        var1 = jt[0]
        self.assertEqual(h1.tag, "h1")
        self.assertEqual(var1.tag, 'jinjavariable')
        self.assertEqual(var1.attrib['value'], 'hi')

    def test_var_2(self):
        html_string = """<h1>{{ a.b }}</h1>"""

        tree = self.parser.parseFragment(html_string)

        h1 = tree[0]
        jt = h1[0]
        var1 = jt[0]
        self.assertEqual(h1.tag, "h1")
        self.assertEqual(var1.tag, 'jinjavariable')
        self.assertEqual(var1.attrib['value'], 'a.b')

    def test_filter_1(self):
        html_string = """<h1>{{ hi | yo }}</h1>"""

        tree = self.parser.parseFragment(html_string)

        h1 = tree[0]
        self.assertEqual(h1.tag, "h1")

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
        html_string = """<h1>{{ hi | yo("hi") }}</h1>"""

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        h1 = tree[0]
        self.assertEqual(h1.tag, "h1")

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

    def test_filter_3(self):
        html_string = """<h1>{{ hi | yo("hi", "mike") }}</h1>"""

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        h1 = tree[0]
        self.assertEqual(h1.tag, "h1")

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
        arg2 = yo[1]

        self.assertEqual(arg1.tag, 'jinjaargument')
        self.assertEqual(arg1.attrib['value'], '"hi"')
        self.assertEqual(arg2.tag, 'jinjaargument')
        self.assertEqual(arg2.attrib['value'], '"mike"')

    def test_jinja_block(self):
        html_string = """
            {% block title %}Hi{% endblock %}
        """

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        block = tree[0]

        self.assertEqual(block.tag, 'jinjablock')
        self.assertEqual(block.text, 'Hi')

    def test_jinja_block_in_title(self):
        html_string = """
        <title>{% block title %}{% endblock %}</title>
        """

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        title = tree[0]
        block = title[0]

        self.assertEqual(title.tag, 'title')
        self.assertEqual(block.tag, 'jinjablock')
        self.assertEqual(block.attrib['value'], 'title')

    def test_jinja_for(self):
        html_string = """
            {% for a in b %}
                {{ a }}
            {% endfor %}
        """

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        block = tree[0]
        var = block[0]
        var1 = var[0]

        self.assertEqual(block.tag, 'jinjafor')
        self.assertEqual(block.attrib['value'], 'a in b')
        self.assertEqual(var.tag, 'jinjavariabletag')
        self.assertEqual(var1.tag, 'jinjavariable')
        self.assertEqual(var1.attrib['value'], 'a')
