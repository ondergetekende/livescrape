Introduction
============

`livescrape` is a tool for building pythonic web scrapers. Contrary to other scrapers, it focusses on exposing the scraped site in a semantic way in your application. It allows you to define page objects, specifying infomation to be extracted, and how to navigate to other page objects.

While other scraping libraries would mostly be used in batch jobs, `livescrape` is intended to be used in the main application.

Defining a scraper
==================

Defining a scraper is similar to defining a model in django. In my example I'll use github. Github has an API which would be far more suitable for any use, but it's a well-known site, which helps understanding the examples.

Let's start by defining github's repository page

    from livescrape import ScrapedPage, Css
    
    class GithubProjectpage(ScrapedPage):
        scrape_url = "https://github.com/python/cpython/"
    
        description = Css(".repository-meta-content")
    
    page = GithubProjectpage()
    print(page.description)
    # will output the description

That's nice and all, but we don't just want to address the project page for the cpython mirror, but just any project page. We can do this by adding string formatting parameters to `scrape_url`.

    from livescrape import ScrapedPage, Css
    
    class GithubProjectpage(ScrapedPage):
        scrape_url = "https://github.com/%(username)s/%(projectname)s/"
    
        description = Css(".repository-meta-content")
    
    page = GithubProjectpage(username="python", projectname="cpython")
    print(page.description)
    # will output the description

You can avoid using keyword arguments by defining `scrape_args` like this:

    from livescrape import ScrapedPage, Css
    
    class GithubProjectpage(ScrapedPage):
        scrape_url = "https://github.com/%(username)s/%(projectname)s/"
        scrape_args = ("username", "projectname")
    
        description = Css(".repository-meta-content")
    
    page = GithubProjectpage("python", "cpython")
    print(page.description)
    # will output the description


Cleaning up the data
====================

Now when you run the previous example, you may notice that the description is padded with a lot of whitespace. We really don't want that, so we can add a `cleanup` function. The signature is `cleanup(text_content, element)`. In this example I'll use a lambda.

    from livescrape import ScrapedPage, Css
    
    class GithubProjectpage(ScrapedPage):
        scrape_url = "https://github.com/%(username)s/%(projectname)s/"
        scrape_args = ("username", "projectname")
    
        description = Css(".repository-meta-content", 
                          cleanup=lambda value, element: value.strip())
    
    page = GithubProjectpage("python", "cpython")
    print(page.description)
    # will output the description

Often, you'll need to do something more complicated, like further parsing a string. A lambda would be too cramped fo that. In that case, it may be useful to declare the cleanup function using the decorator syntax:

    from livescrape import ScrapedPage, Css
    
    class GithubProjectpage(ScrapedPage):
        scrape_url = "https://github.com/%(username)s/%(projectname)s/"
        scrape_args = ("username", "projectname")
    
        @Css(".repository-meta-content")
        def description(self, value, element):
            return value.strip()
    
    page = GithubProjectpage("python", "cpython")
    print(page.description)
    # will output the description

For some common datatypes, there are special `Css` selectors: `CssInt`, `CssFloat`, `CssDate` , `CssRaw` (for raw html) and `CssBoolean` (testing whether some selector is present).


List data
=========

Normaly when scraping, only the first matching element is used, but sometimes you'll want to go over lists of things. To do so, specify the `multiple` argument. In this example contents will produce the names of all the root directories in the project.

    from livescrape import ScrapedPage, Css
    
    class GithubProjectpage(ScrapedPage):
        scrape_url = "https://github.com/%(username)s/%(projectname)s/"
        scrape_args = ("username", "projectname")
        
        contents = Css('.js-directory-link', multiple=True)

Note that cleanup code runs per list item, not on the list as a whole.

Tabular data
============

If you need more than one datum per list item, you will need to use `CSSMulti`. You can provide the additional selectors as keyword arguments. It will produce a dict with values for each of the table contents.

    from livescrape import ScrapedPage, Css, CssMulti
    
    class GithubProjectpage(ScrapedPage):
        scrape_url = "https://github.com/%(username)s/%(projectname)s/"
        scrape_args = ("username", "projectname")
    
        table_contents = CssMulti(
            'tr.js-navigation-item',
            name=Css("td.content a"),
            message=Css("td.message a"),
            age=Css("td.age time", attribute="datetime"),
            )

Note that cleanup code runs per list item, not on the list as a whole.

Links
=====

Websites typically have links, which you'll want to follow. The `CssLink` selector helps you by allowing you to specify what `ScrapedPage` should handle the target of that link. In the following example, we're reusing one of the `GithubProjectpage` definitions above.

    from scrape import ScrapedPage, CssLink
    
    class GithubOveriew(ScrapedPage):
        scrape_url = "https://github.com/%(username)s"
        scrape_args = ("username")
        
        repos = CssLink(".repo-list-name a", GithubProjectpage, multiple=True)

You could now type `GithubOverview("python").repos[0].description` to retrieve the description of the first repository on the overview page.

Custom HTTP
===========

In many cases, you'll want to customize your HTTP access, for example to add caching, throttling or authentication. To do that, override the `scrape_fetch(url)` method, and add your logic there. You'll need to return a string with the raw HTML.


