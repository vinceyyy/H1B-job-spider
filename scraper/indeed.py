import requests
import lxml.html
import re
import os
import random
import pandas as pd


class Page:
    """request url and parse html for all pages"""

    def __init__(self, url):
        # Load the user agent list once only.
        USER_AGENT_LIST_FILE = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "user_agent_list.txt")
        )
        USER_AGENT_LIST = []
        with open(USER_AGENT_LIST_FILE) as file:
            for line in file:
                li = line.strip()
                if li and not li.startswith("#"):
                    USER_AGENT_LIST.append(line.rstrip("\n"))
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/webp,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, sdch, br",
            "accept-language": "en-GB,en-US;q=0.8,en;q=0.6",
            "upgrade-insecure-requests": "1",
            "user-agent": random.choice(USER_AGENT_LIST),
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
        self.url = url

        if "limit=50" not in self.url:
            self.url = self.url + "&limit=50"
        if "fromage=30" not in self.url:
            self.url = self.url + "&fromage=30"
        self.html = requests.get(url, headers=self.headers).content
        self.tree = lxml.html.fromstring(self.html)
        self.domain = re.search("(https:\/\/.+.com).+", url).group(1)
        self.max_on_page = 50


class JobList(Page):
    """for the page with jobs listed

    Args:
        Page (str): the first page of page list
    """

    def total_num_of_pages(self) -> int:
        """Calculates the number of pages of job listings to be scraped.
        i.e. your search yields 230 results at 50 res/page -> 5 pages of jobs
        only starts from the first page

        Returns:
            The number of pages rest.
        """
        all_num = self.tree.cssselect("#searchCountPages")[0].text_content()
        all_num = int(re.findall(r"(\d+) ", all_num.replace(",", ""))[1])
        number_of_pages = int(all_num) // self.max_on_page
        if number_of_pages == 0:
            return 1
        else:
            return number_of_pages

    def current_num_of_pages(self) -> int:
        """get the current page number

        Returns:
            int: current page number
        """
        cur_num = self.tree.cssselect("#searchCountPages")[0].text_content()
        cur_num = int(re.findall(r"(\d+) ", cur_num.replace(",", ""))[0])
        return cur_num

    def rest_num_of_pages(self) -> int:
        """get number of rest of pages

        Returns:
            int: number of rest pages
        """
        return self.total_num_of_pages() - self.current_num_of_pages()

    def nextpage(self):
        """get the next page url

        Returns:
            str: url of next page
        """
        print(self.url)
        if "start=" not in self.url:
            url = self.url + "&" + f"start={self.max_on_page}"
        else:
            cur_offset = int(re.search(r".*?start=(\d{1,4}).*?", self.url).group(1))
            next_offset = str(cur_offset + self.max_on_page)
            url = re.sub(
                r"(https:\/\/.*&start=)(?:\d{1,4}|\d{1,4}(&.*))",
                rf"\g<1>{next_offset}\g<2>",
                self.url,
            )
            print("next page: ", url)
        return url

    def get_job_index(self):
        """get job index of current page

        Returns:
            pd.DataFrame: job titles and urls df
        """
        urls = [
            i.get("href")
            for i in self.tree.cssselect(
                ".jobsearch-SerpJobCard h2.title a[target=_blank]"
            )
        ]
        urls = [
            "https://www.indeed.com" + url if (url.startswith("/")) else url
            for url in urls
        ]
        titles = [
            i.text_content()
            for i in self.tree.cssselect(
                ".jobsearch-SerpJobCard h2.title a[target=_blank]"
            )
        ]
        return pd.DataFrame({"url": urls, "title": titles})


class JobDetail(Page):
    def title(self):
        return self.tree.cssselect("h1")[0].text_content().strip()

    def company(self):
        return (
            self.tree.cssselect("div.jobsearch-InlineCompanyRating > div")[0]
            .text_content()
            .strip()
        )

    def location(self):
        location = (
            self.tree.cssselect(
                "div.jobsearch-JobInfoHeader-subtitle > div:last-child"
            )[0]
            .text_content()
            .strip()
        )
        if location == "Remote":
            location = (
                self.tree.cssselect(
                    "div.jobsearch-JobInfoHeader-subtitle > div:nth-last-child(2)"
                )[0]
                .text_content()
                .strip()
            )
        return location

    def description(self):
        description = self.tree.cssselect("div#jobDescriptionText")
        if len(description) > 0:
            for br in description[0]:  # replace <br> with \n
                br.tail = "\n" + br.tail if br.tail else "\n"
            description = description[0].text_content()
        return description


if __name__ == "__main__":
    pagelist = JobList("https://www.indeed.com/jobs?q=h1b&limit=50")
    print(pagelist.nextpage())

    while True:
        for url in pagelist.get_job_urls()[:3]:
            job = JobDetail(url)
            print("================================================")
            print(job.title())
            print(job.company())
            print(job.location())
            print("================================================")
            print(job.description())
        break