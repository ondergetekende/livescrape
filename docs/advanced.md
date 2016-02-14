# Advanced document retrieval

## Introduction

Livescrape comes with a simple `requests`-based document retrieval, defined in `scrape_fetch`. The default implementation retrieves a page using a shared session (`livescrape.SHARED_SESSION`) to retrieve documents via a simple get request.

Sometimes, this is not enough. You may need authentication, post or may want to add some caching to reduce load on the remote server.

# Recipes

In your `ScrapedPage` derived class, you can define your own `scrape_fetch` function, which does whatever you need it to do. It should return the unicode for the page.

## Post requests

Implementations of scrape_fetch are not limited to just get requests, you can also use posts. In that case, you probably need more arguments than just those those for the url template. You can just define some additional scrape arguments (along with any default values). They will end up in `scrape_args` after the `ScrapedPage` is constructed.

    import livescrape, os
    
    class MyCustomScrapedPage(livescrape.ScrapedPage):
        scrape_url = "http://example.net/search"
        scrape_args = ['query']
    
        def scrape_fetch(self, url):
            query = self.scrape_args['query']
            response = self.scape_session.post(url, data={'q': query})
            return response.text

## Authentication

Many sites require some sort of authentication. The easiest way to do authentication is just to try to request the target page, detect if you need to log in, optionally log in, and try again. Using a session persistance is necessary to keep the number of logins down.

    import livescrape, requests
    
    class MyCustomScrapedPage(livescrape.ScrapedPage):    
        def scrape_fetch(self, url):
            response = self.scrape_session.get(text, allow_redirect=False)
            if (response.status_code == 302 or  # redirect to login page
                    response.status_code == 403 or  # HTTP forbidden
                    "Anonymous user" in response.text):  # Somthing in the page
                self.scrape_session.post("http://example.net/login",
                                         data={"username": "JohnDoe",
                                               "password": "hunter2"})
                response = self.scrape_session.get(text, allow_redirect=False)
            return response.text


You may also need to add stuff like csfr token retrieval, but that's left as an excersise for the reader.

## Caching

When you're using a site as an API, you typically repeat the same request over and over again. Adding some sort of caching may reduce the impact on the remote site. In this example I'll use the django caching framework, but this could easilly be adapted for other caching methods.

    import livescrape, requests
    from django.core.cache import cache
    
    class MyCustomScrapedPage(livescrape.ScrapedPage):    
        def scrape_fetch(self, url):
            cache_key = "some_prefix:" + url
            page = cache.get(cache_key)
            if not page:
                page = super(MyCustomScrapedPage, self).scrape_fetch(url)
                cache.set(cache_key, page, 3600)
            return page

## Local documents

When you have a local copy of a site (say, you downloaded an archive), you needn't use the requests library, you just need to turn the url into a filename, and read the file from disk. Remember that you need to perform unicode decoding as well.

    import livescrape, os
    
    class MyCustomScrapedPage(livescrape.ScrapedPage):    
        def scrape_fetch(self, url):
            file = url.split('/')[-1]
            with open(os.path.join("my_archive", file), "rb") as f:
                page = r.read()
            return page.decode('utf8')
