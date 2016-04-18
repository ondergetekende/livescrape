from livescrape import ScrapedPage, Css, CssGroup, CssLink


class GithubProjectpage(ScrapedPage):
    scrape_url = "https://github.com/%(username)s/%(projectname)s/"
    scrape_args = ("username", "projectname")

    description = Css(".repository-meta-content",
                      cleanup=lambda desc: desc.strip())
    contents = CssLink('.js-directory-link', "GithubOveriew", multiple=True)
    table_contents = CssGroup('tr.js-navigation-item', multiple=True)
    table_contents.name = Css("td.content a")
    table_contents.message = Css("td.message a")
    table_contents.age = Css("td.age time", attribute="datetime")


class GithubOveriew(ScrapedPage):
    scrape_url = "https://github.com/%(username)s"
    scrape_args = ("username")

    repos = CssLink(".repo-list-name a", GithubProjectpage, multiple=True)


if __name__ == '__main__':
    cpython = GithubOveriew(username="python")
    print(cpython.repos[0].description)
    print(cpython.repos[0].description)
