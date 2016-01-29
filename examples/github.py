from livescrape import ScrapedPage, Css, CssMulti, CssLink


class GithubProjectpage(ScrapedPage):
    scrape_url = "https://github.com/%(username)s/%(projectname)s/"
    scrape_args = ("username", "projectname")

    description = Css(".repository-meta-content",
                      cleanup=lambda desc: desc.strip())
    contents = CssMulti('.js-directory-link')
    table_contents = CssMulti(
        'tr.js-navigation-item',
        name=Css("td.content a"),
        message=Css("td.message a"),
        age=Css("td.age time", attribute="datetime"),
    )


class GithubOveriew(ScrapedPage):
    scrape_url = "https://github.com/%(username)s"
    scrape_args = ("username")

    repos = CssLink(".repo-list-name a", GithubProjectpage, multiple=True)


if __name__ == '__main__':
    cpython = GithubOveriew(username="python")
    print(cpython.repos[0].description)
