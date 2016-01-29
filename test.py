import unittest

import livescrape


class BasePage(livescrape.ScrapedPage):
    scrape_url = "http://localhost/fake"

    def scrape_fetch(self, url):
        return """<html><body>
            <h1 class="foo" data-foo=1>Heading</h1>
            <h1 id="the-id">15</h1>
            <span class=float>3.14</span>
            <span class=int>42</span>
            <span class=bool></span>
            <span class=date>2016-04-23</span>
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

    def test_dict(self):
        class Page(BasePage):
            foo = livescrape.Css("h1.foo")

        x = Page()

        self.assertEqual(x._dict, {"foo": 'Heading'})

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

    def test_float(self):
        class Page(BasePage):
            foo = livescrape.CssFloat(".float")

        x = Page()

        self.assertAlmostEqual(x.foo, 3.14)

    def test_int(self):
        class Page(BasePage):
            foo = livescrape.CssInt(".int")

        x = Page()

        self.assertEqual(x.foo, 42)

    def test_date(self):
        class Page(BasePage):
            foo = livescrape.CssDate(".date", '%Y-%m-%d')

        x = Page()

        self.assertEqual(x.foo.year, 2016)

    def test_bool(self):
        class Page(BasePage):
            foo = livescrape.CssBoolean(".bool")
            bar = livescrape.CssBoolean(".bool-not-there")

        x = Page()

        self.assertTrue(x.foo)
        self.assertFalse(x.bar)

    def test_raw(self):
        class Page(BasePage):
            foo = livescrape.CssRaw("table>tr")

        x = Page()

        self.assertEqual(x.foo, "<th>key</th><td>value</td>")

    def test_complex(self):
        class Page(BasePage):
            foo = livescrape.CssMulti(
                "table tr",
                key=livescrape.Css("th"),
                value=livescrape.Css("td"))

        x = Page()

        self.assertEqual(x.foo, [{"key": "key", "value": "value"},
                                 {"key": "key2", "value": "value2"}])

    def test_cleanup(self):
        cleanup_args = [None]

        def cleanup(x):
            self.assertIsNone(cleanup_args[0])
            cleanup_args[0] = x
            return "TESTed"

        class Page(BasePage):
            foo = livescrape.Css("h1.foo",
                                 cleanup=cleanup)

        x = Page()

        self.assertEqual(x.foo, "TESTed")
        self.assertEqual(cleanup_args[0], "Heading")

    def test_extract(self):
        extract_args = [None]

        def extract(x):
            self.assertIsNone(extract_args[0])
            extract_args[0] = x
            return "TESTed"

        class Page(BasePage):
            foo = livescrape.Css("h1.foo",
                                 extract=extract)

        x = Page()

        self.assertEqual(x.foo, "TESTed")
        self.assertEqual(extract_args[0].text, "Heading")

    def test_cleanup_extract(self):
        cleanup_args = [None]
        extract_args = [None]

        def cleanup(x):
            self.assertIsNone(cleanup_args[0])
            cleanup_args[0] = x
            return "TESTed"

        def extract(x):
            print("XXX", repr(x))
            self.assertIsNone(extract_args[0])
            extract_args[0] = x
            return "Xtracted"

        class Page(BasePage):
            foo = livescrape.Css("h1.foo",
                                 cleanup=cleanup,
                                 extract=extract)

        x = Page()
        value = x.foo

        self.assertEqual(extract_args[0].text, "Heading")
        self.assertEqual(cleanup_args[0], "Xtracted")
        self.assertEqual(value, "TESTed")

    def test_decorator(self):
        cleanup_args = [None]
        extract_args = [None]
        method_args = [None]

        def cleanup(x):
            self.assertIsNone(cleanup_args[0])
            cleanup_args[0] = x
            return "TESTed"

        def extract(x):
            print("XXX", repr(x))
            self.assertIsNone(extract_args[0])
            extract_args[0] = x
            return "Xtracted"

        class Page(BasePage):
            @livescrape.Css("h1.foo",
                            cleanup=cleanup,
                            extract=extract)
            def foo(self, value, element):
                method_args[0] = (value, element)
                return "METhod"

        x = Page()
        value = x.foo

        self.assertEqual(extract_args[0].text, "Heading")
        self.assertEqual(cleanup_args[0], "Xtracted")
        self.assertEqual(method_args[0][0], "TESTed")
        self.assertEqual(method_args[0][1].text, "Heading")
        self.assertEqual(value, "METhod")

if __name__ == '__main__':
    unittest.main()
