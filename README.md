[![Build Status](https://travis-ci.org/ondergetekende/livesscrape.png?branch=master)](https://travis-ci.org/ondergetekende/livesscrape)
[![PyPI version](https://badge.fury.io/py/livescrape.svg)](https://pypi.python.org/pypi/livescrape)
[![Documentation](https://readthedocs.org/projects/readthedocs/badge/?version=latest)](https://livesscrape.readthedocs.org/en/latest/)

Introduction
============

`livescrape` is a tool for building pythonic web scrapers. Contrary to other scrapers, it focusses on exposing the scraped site in a semantic way in your application. It allows you to define page objects, specifying infomation to be extracted, and how to navigate to other page objects.

While other scraping libraries would mostly be used in batch jobs, `livescrape` is intended to be used in the main application.

Example
=======

For more complete example, I recommend you check out the [Tutorial](docs/tutorial.md), but here's a quick primer using github.
 
    from livescrape import ScrapedPage, Css, CssMulti
    
    class GithubProjectPage(ScrapedPage):
        scrape_url = "https://github.com/%(username)s/%(projectname)s/"
        scrape_args = ("username", "projectname")
    
        description = Css(".repository-meta-content",
                          cleanup=lambda desc: desc.strip())
        contents = Css('.js-directory-link', multiple=True)
        table_contents = CssMulti(
            'tr.js-navigation-item',
            name=Css("td.content a"),
            message=Css("td.message a"),
            age=Css("td.age time", attribute="datetime"),
        )
    
    project_page = GithubProjectPage("ondergetekende", "livescrape")
    print(project_page.description)
    # Prints out the description for this project
    
    print(project_page.contents)
    # Prints the filenames in the root of the repository
    
    print(project_page.table_contents)
    # Prints information for all files in the root of the repository
