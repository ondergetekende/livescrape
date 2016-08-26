# API documentation

## ScrapedPage

Under normal circumstances, you'd derive a class of ScrapedPage. ScapedPage converts any `ScrapedAttribute`s to properties which perform the actual scraping.

### scrape_url

The url for the scraped page. Can contain named percent-style formatting placeholders. e.g. `http://localhost:8000/%(directory)s/%(filename)s?q=%(querystring)s`. You will need to pre-encode any parameters you pass in - there is no automatic encoding of parameters

### scrape_args

Names of the positional arguments. After construction, this is replaced by a dictionary with all of the provided values.

### scrape_arg_defaults

Default values for any arguments provided.

### scrape_headers

Defines additional headers to be sent. You may, for example, want to modify the user agent by adding `scrape_headers = {'User-Agent': 'My fake browser'}` to your `ScrapedPage` definition.

### scrape_fetch(self, url)

Fetches the raw HTML for the `ScrapedPage`. In many cases, you'll want to customize your HTTP access, for example to add caching, throttling or authentication. To do that, override the `scrape_fetch(url)` method, and add your logic there. You'll need to return a unicode string with the raw HTML. Any character encodings should already have been applied.

### scrape_create_document(self, raw_html)

Creates a lxml document from the raw html. Sometimes, your document isn't actually HTML, it may have been encoded in some form. In that case, you can override this.

### _dict

A property which returns all of the defined scrape properties in dictionary form.

### scrape_keys

A list of all the scrapable attributes. Automatically generated.

### scrape_session

By default this property returns the session shared by all the `ScrapedPage` classes, but individual classes can override according to their needs. The original shared session can be found in `livescrape.SHARED_SESSION`.

## ScrapedAttribute(extract=None, cleanup=None, attribute=None, multiple=False)

This is the base class for all scraped attributes. 

When `extract` is provided, it is used to extract data from a element which has been selected for. The signature is `extract(element)`.

when `attribute` is provided, the data is extracted from the named attribute, instead of the element's text. Cannot be used together with `extract`.

When `cleanup` is provided, it is called on the extracted data just before it is returned. The signature is `cleanup(extracted_data)`

When `multiple` is provided, not just the first matching element is converted, but all of them. As a result, the attribute returns an iterable, even when only one element is selected. `cleanup` and `extract` are still applied per-element.

### extract(self, element, scraped_document)

Pulls data from the provided element. This can be overridden to create attributes which aren't simply based on the element text or attribute. For one-off jobs, you may want to use the `extract=` argument in the constructor.

### cleanup(self, extracted_data, element)

Converts the extracted data into usable data. This can be overridden to create type-specific extractors. For one-off jobs, you may want to use the `cleanup=` argument in the constructor.

### @decorator
`ScrapedAttribute` can be used as a decorator. The decorated function functions as both cleanup and extract. It's signature is `attribute_name(value, element)`.

## Specialized selectors
### Css(selector, ...)

Pulls data from the document using a `selector`, and returns it as a string.
Supports all additional constructor arguments defined by `ScrapedAttribute`. If you pass an empty string, the entire document will be used. (useful in combination with `CssGroup`)

## CssFloat(selector, ...)

Pulls data from the document using a css selector, and converts it to a floating point number. Supports all additional constructor arguments defined by `ScrapedAttribute`.

## CssInt(selector, ...)

Pulls data from the document using a css selector, and converts it to an integer. Supports all additional constructor arguments defined by `ScrapedAttribute`. 

## CssDate(selector, ...)

Pulls data from the document using a css selector, and converts it to an datetime object, using the second parameter (`date_format`). Supports all additional constructor arguments defined by `ScrapedAttribute`.

## CssBoolean(selector)

Pulls data from the document using a css selector, and returns true if it was found. Supports none of the additional constructor arguments defined by `ScrapedAttribute`.

## CssRaw(selector, ...)

Pulls data from the document using a css selector, and returns the content's raw html. Not that this HTML has been fixed up by lxml, and may differ from the html in the original document. Supports all additional constructor arguments defined by `ScrapedAttribute`, except `extract`.

## CssGroup(selector)

Groups together several attributes, which all operate on the same element. Especially useful when used with`multiple=True`. Adding an element is done by assigning an `ScrapedAttribute` to an attribute of CssGroup, like this:

```python
from livescrape import ScrapedPage, CssGroup, Css

class SomePage(ScrapedPage):
    user = CssGroup(".user")
    user.name = Css("a.username")  # Effectively finds ".user a.username"
    user.rank = Css("a.userrank")
```

## CssMulti(selector, attr1=..., attr2=... )

Finds a list of elements in the document, and for each element, applies additional `ScrapedAttribute`s to build a dictionary. The additional attributes are provided as keyword arguments to the constructor. Supports none of the additional constructor arguments defined by `ScrapedAttribute`.

Deprecated in favor of `CssGroup`

## CssLink(selector, page_type, referer=True, ...)

Finds links in the document using `selector`, and returns a new `ScrapedPage` for the link target. `page_type` is the type of `ScrapedPage` to be instantiated. You may pass the target type by name, to break circular dependencies. Supports all additional constructor arguments defined by `ScrapedAttribute`, although by default, it defines `attribute='href'` for obvious reasons.

If `referer` is True, the Referer header is set up automatically. You can also set it to a custom url, or to False (for no referer header).

# SHARED_SESSION

All of the `ScapedPage` descendents share a [requests](http://docs.python-requests.org/) session. In the classes this is exposed in an overridable `scrape_session` property. It may be tempting to change things in the shared session, such as user agent, however, as with any global variable, this is a bad idea. Libraries using livescrape may depend on the default values, and may break when you change them. If you need a custom session, it is best to override the `scrape_session` property to provide your own one.

Forward compatibility
=====================

This project uses [semantic versioning](http://semver.org/). Names starting with `scrape_`  and underscore (`_`) are reserved. You should not define attribibutes by those names.
