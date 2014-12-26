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
        self.parser = html5lib.HTMLParser(strict=True, namespaceHTMLElements=False)

    def test_var_1(self):
        html_string = """<h1>{{ hi }}</h1>"""

        tree = self.parser.parseFragment(html_string)

        self.assertTree(tree, [{
            'tag': 'h1',
            'children': [{
                'tag': 'jinjavariabletag',
                'children': [{
                    'tag': 'jinjavariable',
                    'value': 'hi'
                }]
            }]
        }])

    def test_var_2(self):
        html_string = """<h1>{{ a.b }}</h1>"""

        tree = self.parser.parseFragment(html_string)

        self.assertTree(tree, [{
            'tag': 'h1',
            'children': [{
                'tag': 'jinjavariabletag',
                'children': [{
                    'tag': 'jinjavariable',
                    'value': 'a.b'
                }]
            }]
        }])

    def test_filter_1(self):
        html_string = """<h1>{{ hi | yo }}</h1>"""

        tree = self.parser.parseFragment(html_string)

        self.assertTree(tree, [{
            'tag': 'h1',
            'children': [{
                'tag': 'jinjavariabletag',
                'children': [{
                    'tag': 'jinjavariable',
                    'value': 'hi'
                }, {
                    'tag': 'jinjapipe',
                    'value': '|'
                }, {
                    'tag': 'jinjafilter',
                    'value': 'yo'
                }]
            }]
        }])

    def test_filter_2(self):
        html_string = """<h1>{{ hi | yo("hi") }}</h1>"""

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        self.assertTree(tree, [{
            'tag': 'h1',
            'children': [{
                'tag': 'jinjavariabletag',
                'children': [{
                    'tag': 'jinjavariable',
                    'value': 'hi'
                }, {
                    'tag': 'jinjapipe',
                    'value': '|'
                }, {
                    'tag': 'jinjafilter',
                    'value': 'yo',
                    'children': [{
                        'tag': 'jinjaargument',
                        'value': '"hi"'
                    }]
                }]
            }]
        }])

    def test_filter_3(self):
        html_string = """<h1>{{ hi | yo("hi", "mike") }}</h1>"""

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        self.assertTree(tree, [{
            'tag': 'h1',
            'children': [{
                'tag': 'jinjavariabletag',
                'children': [{
                    'tag': 'jinjavariable',
                    'value': 'hi'
                }, {
                    'tag': 'jinjapipe',
                    'value': '|'
                }, {
                    'tag': 'jinjafilter',
                    'value': 'yo',
                    'children': [{
                        'tag': 'jinjaargument',
                        'value': '"hi"'
                    }, {
                        'tag': 'jinjaargument',
                        'value': '"mike"'
                    }]
                }]
            }]
        }])

    def test_jinja_block(self):
        html_string = """
            {% block title %}Hi{% endblock %}
        """

        tree = self.parser.parseFragment(html_string)

        self.assertTree(tree, [{
            'tag': 'jinjablock',
            'text': 'Hi'
        }])

    def test_jinja_block_in_title(self):
        html_string = """
        <title>{% block title %}{% endblock %}</title>
        """

        tree = self.parser.parseFragment(html_string)

        self.assertTree(tree, [{
            'tag': 'title',
            'children': [{
                'tag': 'jinjablock',
                'value': 'title'
            }]
        }])

    def test_jinja_for(self):
        html_string = """
            {% for a in b %}
                {{ a }}
            {% endfor %}
        """

        tree = self.parser.parseFragment(html_string)

        self.assertTree(tree, [{
            'tag': 'jinjafor',
            'value': 'a in b',
            'children': [{
                'tag': 'jinjavariabletag',
                'children': [{
                    'tag': 'jinjavariable',
                    'value': 'a'
                }]
            }]
        }])

    def test_complete_doc(self):
        html_string = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <title>My Webpage</title>
            </head>
            <body>
                <ul id="navigation">
                {% for item in navigation %}
                    <li><a href="{{ item.href }}">{{ item.caption }}</a></li>
                {% endfor %}
                </ul>

                <h1>My Webpage</h1>
                {{ a_variable }}
            </body>
            </html>
        """

        tree = self.parser.parse(html_string)
        dump(tree)
        self.assertTree(tree, [{
            'tag': 'head',
            'children': [{
                'tag': 'title',
                'text': 'My Webpage'
            }]
        }, {
            'tag': 'body',
            'children': [{
                'tag': 'ul',
                'children': [{
                    'tag': 'jinjafor',
                    'value': 'item in navigation',
                    'children': [{
                        'tag': 'li',
                        'children': [{
                            'tag': 'a',
                            'children': [{
                                'tag': 'jinjavariabletag',
                                'children': [{
                                    'tag': 'jinjavariable',
                                    'value': 'item.caption'
                                }]
                            }]
                        }]
                    }]
                }]
            }, {
                'tag': 'h1',
                'text': 'My Webpage'
            }, {
                'tag': 'jinjavariabletag',
                'children': [{
                    'tag': 'jinjavariable',
                    'value': 'a_variable'
                }]
            }]
        }])

    def test_jinja_if(self):
        html_string = """
            {% if True %}yay{% endif %}
        """

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        self.assertTree(tree, [{
            'tag': 'jinjaif',
            'text': 'yay'
        }])

    def assertTree(self, root, spec):
        self.assertEqual(len(root), len(spec))

        for child, spec_child in zip(root, spec):
            self.assertEqual(child.tag, spec_child['tag'])

            if 'text' in spec_child:
                self.assertEqual(child.text, spec_child['text'])

            if 'value' in spec_child:
                self.assertEqual(child.attrib['value'], spec_child['value'])

            if 'children' in spec_child:
                self.assertTree(child, spec_child['children'])
