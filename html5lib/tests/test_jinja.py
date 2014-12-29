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

    def test_open_block(self):
        html_string = """
            <div class="basket-site dropdown-menu" role="menu">
                {% set cart = active_cart() %}
                {% for cart_product in cart.products %}
                {% endfor %}

                <div class="controls clearfix">
            {#
                    <button type="button" class="btn btn-link">VIEW BASKET</button>
            #}
                </div>
            </div>
        """
        tree = self.parser.parseFragment(html_string)
        dump(tree)
