Introduction
============

`livescrape` is a tool for building pythonic web scrapers. Contrary to other scrapers, it focusses on exposing the scraped site in a semantic way in your application. It allows you to define page objects, specifying infomation to be extracted, and how to navigate to other page objects.

While other scraping libraries would mostly be used in batch jobs, `livescrape` is intended to be used in the main application. `livescrape` turns the human interface into an API.

Example
=======

For more complete example, I recommend you check out the [Tutorial](tutorial.md), but here's a quick primer using github.

    class GithubProjectpage(ScrapedPage):
        scrape_url = "https://github.com/%(username)s/%(projectname)s/"
        scrape_args = ("username", "projectname")
    
        description = Css(".repository-meta-content",
                          cleanup=lambda desc: desc.strip())
        contents = Css('.js-directory-link', multiple=True)
        table_contents = CssGroup('tr.js-navigation-item')
        table_contents.name = Css("td.content a")
        table_contents.message = Css("td.message a")
        table_contents.age = Css("td.age time", attribute="datetime"),
    
    project_page = GithubProjectPage("ondergetekende", "livescrape")
    
    print(project_page.description) # Prints the description for this project
        
    print(projects.contents)  # Prints the filenames in the repository root
