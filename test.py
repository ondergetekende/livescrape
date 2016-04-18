import responses
import unittest2 as unittest

import livescrape


class BasePage(livescrape.ScrapedPage):
    scrape_url = "http://fake-host/test.html"


class Test(unittest.TestCase):
    def setUp(self):
        responses.reset()
        responses.add(
            responses.GET, BasePage.scrape_url,
            """<html><body>
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
            """)
        responses.start()
        self.addCleanup(responses.stop)

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
            not_there = livescrape.Css("h1.foo",
                                       attribute="not-there")

        x = Page()

        self.assertEqual(x.foo, '1')
        self.assertIsNone(x.not_there)

    def test_link(self):
        class Page(BasePage):
            foo = livescrape.CssLink("a", "Page")

        x = Page()

        self.assertIsInstance(x.foo, Page)
        self.assertEqual(x.foo.scrape_url,
                         "http://fake-host/very-fake")

    def test_float(self):
        class Page(BasePage):
            foo = livescrape.CssFloat(".float")
            foo_fail = livescrape.CssFloat(".date")

        x = Page()

        self.assertAlmostEqual(x.foo, 3.14)
        self.assertIsNone(x.foo_fail)

    def test_int(self):
        class Page(BasePage):
            foo = livescrape.CssInt(".int")
            foo_fail = livescrape.CssInt(".date")

        x = Page()

        self.assertEqual(x.foo, 42)
        self.assertIsNone(x.foo_fail)

    def test_date(self):
        class Page(BasePage):
            foo = livescrape.CssDate(".date", '%Y-%m-%d')
            foo_fail = livescrape.CssDate(".float", '%Y-%m-%d')

        x = Page()

        self.assertEqual(x.foo.year, 2016)
        self.assertIsNone(x.foo_fail)

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

    def test_group(self):
        class Page(BasePage):
            foo = livescrape.CssGroup("table tr", multiple=True)
            foo.key = livescrape.Css("th")
            foo.value = livescrape.Css("td")

        x = Page()

        self.assertEqual(x.foo[0]["key"], "key")
        self.assertEqual(x.foo[0]["value"], "value")
        self.assertEqual(x.foo[1]["key"], "key2")
        self.assertEqual(x.foo[1]["value"], "value2")

        self.assertEqual(x.foo[0].key, "key")
        self.assertEqual(x.foo[0].value, "value")
        self.assertEqual(x.foo[1].key, "key2")
        self.assertEqual(x.foo[1].value, "value2")
        self.assertEqual(x.foo[0]._dict(),
                         {"key": "key", "value": "value"})

        # List members, but filter private ones
        self.assertEqual([x for x in dir(x.foo[1])
                          if x[0] != "_"],
                         ["key", "value"])

        with self.assertRaises(AttributeError):
            x.foo[0].nonexistent

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

    def test_headers(self):
        class Page(BasePage):
            scrape_headers = {"foo": "bar"}

        Page().scrape_fetch(BasePage.scrape_url)
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.headers['Foo'],
                         'bar')

    def test_referer(self):
        class Page(BasePage):
            foo = livescrape.CssLink("a", "Page")

        x = Page()

        self.assertIsInstance(x.foo, Page)

        responses.add(
            responses.GET, x.foo.scrape_url,
            "<html>")

        self.assertIsNone(x.foo.foo)

        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.headers['Referer'],
                         'http://fake-host/test.html')

    def test_custom_referer(self):
        class Page(BasePage):
            foo = livescrape.CssLink("a", "Page", referer="http://no")

        x = Page()

        self.assertIsInstance(x.foo, Page)

        responses.add(
            responses.GET, x.foo.scrape_url,
            "<html>")

        self.assertIsNone(x.foo.foo)

        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.headers['Referer'],
                         'http://no')

    def test_no_referer(self):
        class Page(BasePage):
            foo = livescrape.CssLink("a", "Page", referer=False)

        x = Page()

        self.assertIsInstance(x.foo, Page)

        responses.add(
            responses.GET, x.foo.scrape_url,
            "<html>")

        self.assertIsNone(x.foo.foo)

        self.assertEqual(len(responses.calls), 2)
        self.assertNotIn("Referer", responses.calls[1].request.headers)

if __name__ == '__main__':
    unittest.main()
