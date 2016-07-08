from abc import abstractmethod
import cgi
import datetime
try:
    import urlparse  # python2
except ImportError:  # pragma: no cover
    import urllib.parse as urlparse
import warnings

import lxml.etree
import lxml.html
import requests
import six


SHARED_SESSION = requests.Session()
SHARED_SESSION.headers['User-Agent'] = "Mozilla/5.0 (Livescrape)"


class ScrapedAttribute(object):
    """Base class for scraped attributes.

    When used in a ScrapedPage, it will be converted into an attribute.
    """

    def __init__(self, extract=None, cleanup=None, attribute=None,
                 multiple=False):
        if extract and attribute:
            raise ValueError("extract and attribute are mututally exclusive")

        self._cleanup = cleanup
        self._extract = extract
        self.attribute = attribute
        self.multiple = multiple

        # Placeholder for cleanup method when using the decorator syntax
        self._cleanup_method = None

    @abstractmethod
    def get(self, doc, scraped_page):  # pragma: no cover
        raise NotImplementedError()

    def extract(self, element, scraped_page):
        if self._extract:
            value = self._extract(element)
        elif self.attribute is None:
            value = element.text_content()
        else:
            value = element.get(self.attribute)
            if value is None:
                return

        # In python2, lxml returns str if only ascii characters are used.
        # This leads to inconsistent return types, so in that case, we convert
        # to unicode (which should be a semantic no-op)
        if six.PY2 and isinstance(value, str):  # pragma: no cover
            value = six.text_type(value)

        return self.perform_cleanups(value, element, scraped_page)

    def perform_cleanups(self, value, element, scraped_page=None):
        if self._cleanup:
            value = self._cleanup(value)

        if self._cleanup_method:
            value = self._cleanup_method(scraped_page, value, element)

        return self.cleanup(value, element, scraped_page)

    def cleanup(self, value, elements, scraped_page=None):
        return value

    def __call__(self, func):
        self._cleanup_method = func
        return self

_SCRAPER_CLASSES = {}


class _ScrapedMeta(type):
    """A metaclass for Scraped.

    Converts any ScrapedAttribute attributes to usable properties.
    """
    def __new__(cls, name, bases, namespace):
        keys = []
        for key, value in namespace.items():
            if isinstance(value, ScrapedAttribute):
                def mk_attribute(selector):
                    def method(scraped):
                        return scraped._get_value(selector)
                    return property(method)

                namespace[key] = mk_attribute(value)
                keys.append(key)

        result = super(_ScrapedMeta, cls).__new__(cls, name, bases, namespace)
        result.scrape_keys = keys
        _SCRAPER_CLASSES[name] = result
        return result


@six.add_metaclass(_ScrapedMeta)
class ScrapedPage(object):
    _scrape_doc = None
    scrape_url = None
    scrape_args = []
    scrape_arg_defaults = {}
    scrape_headers = {}

    def __init__(self, *pargs, **kwargs):
        scrape_url = kwargs.pop("scrape_url", None)
        scrape_referer = kwargs.pop("scrape_referer", None)

        arguments = dict(self.scrape_arg_defaults)
        arguments.update(kwargs)
        arguments.update(zip(self.scrape_args, pargs))
        self.scrape_args = arguments

        if scrape_url:
            self.scrape_url = scrape_url
        elif not self.scrape_url:
            # We can't scrape if we don't actually have a url configured
            raise ValueError("%s.scrape_url needs to be defined" %
                             type(self).__name__)
        else:
            self.scrape_url = self.scrape_url % arguments

        self.scrape_headers = dict(self.scrape_headers)
        if scrape_referer:
            self.scrape_headers['Referer'] = scrape_referer

    @property
    def scrape_session(self):
        return SHARED_SESSION

    def scrape_fetch(self, url):
        return self.scrape_session.get(url,
                                       headers=self.scrape_headers).text

    def scrape_create_document(self, page):
        return lxml.html.fromstring(page)

    def _get_value(self, property_scraper):
        if self._scrape_doc is None:
            page = self.scrape_fetch(self.scrape_url)
            self._scrape_doc = self.scrape_create_document(page)

        return property_scraper.get(self._scrape_doc, scraped_page=self)

    @property
    def _dict(self):
        return dict((key, getattr(self, key)) for key in self.scrape_keys)

    def __repr__(self):
        return "%s(scrape_url=%r)" % (type(self).__name__, self.scrape_url)


class Css(ScrapedAttribute):
    def __init__(self, selector, **kwargs):
        self.selector = selector
        super(Css, self).__init__(**kwargs)

    def get(self, doc, scraped_page):
        assert doc is not None
        elements = doc.cssselect(self.selector)

        if self.multiple:
            values = [self.extract(element, scraped_page)
                      for element in elements]
            return [v for v in values if v is not None]
        elif len(elements):
            return self.extract(elements[0], scraped_page)


class CssFloat(Css):
    def cleanup(self, value, elements, scraped_page=None):
        try:
            return float(value)
        except ValueError:
            return None


class CssInt(Css):
    def cleanup(self, value, elements, scraped_page=None):
        try:
            return int(value)
        except ValueError:
            return None


class CssDate(Css):
    def __init__(self, selector, date_format, tzinfo=None, **kwargs):
        self.date_format = date_format
        self.tzinfo = tzinfo
        super(CssDate, self).__init__(selector, **kwargs)

    def cleanup(self, value, elements, scraped_page=None):
        try:
            result = datetime.datetime.strptime(value, self.date_format)
            if self.tzinfo:
                result = result.replace(tzinfo=self.tzinfo)
            return result
        except ValueError:
            return None


class CssBoolean(Css):
    def cleanup(self, value, elements, scraped_page=None):
        return True


class CssRaw(Css):
    def __init__(self, selector, include_tag=False, **kwargs):
        self.include_tag = include_tag
        super(CssRaw, self).__init__(selector, **kwargs)

    def extract(self, element, scraped_page):
        if self.include_tag:
            value = lxml.html.tostring(element, encoding="unicode")
        else:
            value = six.text_type("")
            if element.text:
                value = cgi.escape(element.text)
            for child in element:
                value += lxml.html.tostring(child, encoding="unicode")

        return self.perform_cleanups(value, element, scraped_page)


class CssMulti(Css):
    def __init__(self, selector, cleanup=None, **subselectors):
        super(CssMulti, self).__init__(selector, cleanup=cleanup,
                                       multiple=True)
        self.subselectors = subselectors
        warnings.warn(
            "The 'CssMulti' class was deprecated in favor of CssGroup",
            DeprecationWarning)

    def extract(self, element, scraped_page=None):
        value = {}

        for key, selector in self.subselectors.items():
            value[key] = selector.get(element,
                                      scraped_page=scraped_page)

        return self.perform_cleanups(value, element, scraped_page)


class CssGroup(Css):
    class _CompoundAttribute(object):
        def __init__(self, parent, element, scraped_page):
            self._subselectors = parent._subselectors
            self._element = element
            self._scaped_page = scraped_page

        def __getattr__(self, attribute):
            try:
                selector = self._subselectors[attribute]
            except KeyError:
                return getattr(super(CssGroup._CompoundAttribute, self),
                               attribute)

            return selector.get(self._element, self._scaped_page)

        def __getitem__(self, attribute):
            # May raise keyerror, which is suitable for __getitem__
            selector = self._subselectors[attribute]
            return selector.get(self._element, self._scaped_page)

        def __dir__(self):
            attrs = dir(super(CssGroup._CompoundAttribute, self))
            attrs += self._subselectors.keys()
            return attrs

        def _dict(self):
            return dict(
                (key, selector.get(self._element, self._scaped_page))
                for (key, selector) in self._subselectors.items())

    def __init__(self, *pargs, **kwargs):
        super(CssGroup, self).__init__(*pargs, **kwargs)
        self._subselectors = {}

    def extract(self, element, scraped_page=None):
        value = CssGroup._CompoundAttribute(self, element, scraped_page)
        return self.perform_cleanups(value, element, scraped_page)

    def __setattr__(self, key, value):
        if isinstance(value, ScrapedAttribute):
            self._subselectors[key] = value
        else:
            super(CssGroup, self).__setattr__(key, value)


class CssLink(Css):
    def __init__(self, selector, page_factory, referer=True, **kwargs):
        super(CssLink, self).__init__(selector, attribute="href", **kwargs)
        self.page_factory = page_factory
        self.referer = referer

    def cleanup(self, value, elements, scraped_page=None):
        url = urlparse.urljoin(scraped_page.scrape_url, value)
        factory = (_SCRAPER_CLASSES[self.page_factory]
                   if isinstance(self.page_factory, six.string_types)
                   else self.page_factory)

        if self.referer is True:  # automatic referer
            referer = scraped_page.scrape_url
        elif not self.referer:
            referer = None
        else:
            referer = self.referer

        return factory(scrape_url=url, scrape_referer=referer)
