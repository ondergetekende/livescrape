import unittest

import livescrape


class BasePage(livescrape.ScrapedPage):
    scrape_url = "http://localhost/fake"

    def scrape_fetch(self, url):
        return """<html><body>
            <h1 class="foo" data-foo=1>Heading</h1>
            <h1 id="the-id">15</h1>
            <a href="/very-fake">link</a>
            <table>
              <tr><th>key<td>value</tr>
              <tr><th>key2<td>value2</tr>
            </table
            """


class Test(unittest.TestCase):

    def test_simplecss(self):
        class Page(BasePage):
            foo = livescrape.Css("h1.foo")

        x = Page()

        self.assertEqual(x.foo, 'Heading')

    def test_ambigous(self):
        class Page(BasePage):
            foo = livescrape.Css("h1")

        x = Page()

        self.assertEqual(x.foo, 'Heading')

    def test_multiple(self):
        class Page(BasePage):
            foo = livescrape.Css("h1",
                                 multiple=True)

        x = Page()

        self.assertEqual(x.foo, ['Heading', '15'])

    def test_attribute(self):
        class Page(BasePage):
            foo = livescrape.Css("h1.foo",
                                 attribute="data-foo")

        x = Page()

        self.assertEqual(x.foo, '1')

    def test_link(self):
        class Page(BasePage):
            foo = livescrape.CssLink("a", "Page")

        x = Page()

        self.assertIsInstance(x.foo, Page)
        self.assertEqual(x.foo.scrape_url,
                         "http://localhost/very-fake")

    def test_complex(self):
        class Page(BasePage):
            foo = livescrape.CssMulti(
                "table tr",
                key=livescrape.Css("th"),
                value=livescrape.Css("td"))

        x = Page()

        self.assertEqual(x.foo, [{"key": "key", "value": "value"},
                                 {"key": "key2", "value": "value2"}])


if __name__ == '__main__':
    unittest.main()
