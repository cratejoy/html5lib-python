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
        self.parser = html5lib.HTMLParser(strict=True, namespaceHTMLElements=False, tree=html5lib.treebuilders.getTreeBuilder("etree", fullTree=True))

    def test_var_1(self):
        html_string = """<h1>{{ hi }}</h1>"""

        tree = self.parser.parseFragment(html_string)
        dump(tree)

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
        dump(tree)

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

        self.assertTree(tree, [{
            'tag': '<!DOCTYPE>',
            'text': 'html'
        }, {
            'tag': 'html',
            'children': [{
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

    def test_jinja_if_lstrip(self):
        html_string = """
            {%+ if True %}yay{% endif %}
        """

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        self.assertTree(tree, [{
            'tag': 'jinjaif',
            'text': 'yay',
            'attrs': {
                'lstrip': False
            }
        }])

    def test_jinja_strip_blocks(self):
        html_string = """
            {% for item in seq -%}
                {{ item }}
            {%- endfor %}
        """

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        self.assertTree(tree, [{
            'tag': 'jinjafor',
            'attrs': {
                'rstrip': True
            },
            'children': [{
                'tag': 'jinjavariabletag',
                'children': [{
                    'tag': 'jinjavariable',
                    'value': 'item'
                }]
            }]
        }])

    def test_jinja_extend(self):
        html_string = """
            {% extends "base.html" %}
        """

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        self.assertTree(tree, [{
            'tag': 'jinjaextends',
            'value': '"base.html"'
        }])

    def test_jinja_include(self):
        html_string = """
            {% include ['special_sidebar.html', 'sidebar.html'] ignore missing %}
        """

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        self.assertTree(tree, [{
            'tag': 'jinjainclude',
            'value': "['special_sidebar.html', 'sidebar.html'] ignore missing"
        }])

    def test_jinja_import(self):
        html_string = """
            {% import 'forms.html' as forms %}
            {% from 'forms.html' import input as input_field, textarea %}
        """

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        self.assertTree(tree, [{
            'tag': 'jinjaimport',
            'value': "'forms.html' as forms"
        }, {
            'tag': 'jinjaimport',
            'value': "'forms.html' import input as input_field, textarea"
        }])

    def test_inline_if(self):
        html_string = """
            {{ '[%s]' % page.title if page.title }}
        """

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        self.assertTree(tree, [{
            'tag': 'jinjavariabletag',
            'children': [{
                'tag': 'jinjavariable',
                'value': "'[%s]'"
            }, {
                'tag': 'jinjavariable',
                'value': "%"
            }, {
                'tag': 'jinjavariable',
                'value': "page.title"
            }, {
                'tag': 'jinjavariable',
                'value': "if"
            }, {
                'tag': 'jinjavariable',
                'value': "page.title"
            }]
        }])

    def test_comment(self):
        html_string = """
            {# {{ '[%s]' % page.title if page.title }} #}
        """

        tree = self.parser.parseFragment(html_string)
        dump(tree)

        self.assertTree(tree, [{
            'tag': 'jinjacomment',
            'value': "{{ '[%s]' % page.title if page.title }} "
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
            else:
                self.assertEqual(len(child), 0)

            if 'attrs' in spec_child:
                for k, v in spec_child['attrs'].iteritems():
                    self.assertIn(k, child.attrib)
                    self.assertEqual(v, child.attrib[k])
