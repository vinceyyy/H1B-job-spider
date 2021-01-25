import pandas as pd
from scraper.indeed import JobList, JobDetail
from cleaner.judge import negative_bool
import time
import random


class Manager:
    def __init__(self, website: str, keywords: str):
        """init a manager to keep retrying

        Args:
            website (str): indeed
            keywords (str): keywords with spaces

        Raises:
            ValueError: unsupported website
        """
        self.KEYWORDS = keywords
        self.df = pd.DataFrame(
            columns=["title", "company", "location", "description", "url"]
        )
        if website == "indeed":
            self.url = "https://www.indeed.com/jobs?q=" + self.KEYWORDS.replace(
                " ", "%20"
            )
        else:
            raise ValueError("Only support indeed")

    def build_index(self):
        """if local index exists, load it;
        if not, init a index with job titles and job urls, and also save to local
        """
        try:
            index = pd.read_csv("index.csv")
            print("Index exists. Load index.")
            self.index = index
        except:
            print("No index found. Initialize index.")
            index = pd.DataFrame()
            joblists = JobList(self.url)
            print(f"Start at {joblists.url}")
            print(
                f"Found {joblists.total_num_of_pages()} pages"
            )  # it is ok if this num is wrong

            # in case the nagination system is broken
            signal = joblists.current_num_of_pages()

            while joblists.rest_num_of_pages() >= 0:
                print(f"Current at {joblists.current_num_of_pages()} page")
                index = index.append(joblists.get_job_index(), ignore_index=True)
                time.sleep(random.uniform(0.5, 1))
                if joblists.rest_num_of_pages() == 0:
                    print("last page achieved")
                    print("=============================")
                    break
                else:
                    joblists = JobList(joblists.nextpage())
                    # sometimes indeed's pagination is broken and gives infinite pages
                    if joblists.current_num_of_pages() < signal:
                        print("Pagination is wrong. Break here")
                        print("=============================")
                        break
                    signal = joblists.current_num_of_pages()

                    print(f"remaining pages: {joblists.rest_num_of_pages()}")
            print(f"Total {len(index)} job urls found.")
            self.index = index.reset_index(drop=True)
            self.index.to_csv("index.csv", index=False)

    def get_job_detail(self, url: str):
        """retrive single job detail

        Args:
            url (str): url of single job detail
        """
        job = JobDetail(url)
        output = {
            "title": job.title(),
            "company": job.company(),
            "location": job.location(),
            "description": job.description(),
            "url": url,
        }
        self.df = self.df.append(output, ignore_index=True)

    def if_unfinished(self):
        unfinished_df = self.index[~self.index["url"].isin(self.df["url"].to_list())]
        if len(unfinished_df) > 0:
            return True

    def trying(self, df):
        """try to retrive all unfinished jobs

        Args:
            df (pd.DataFrame): df of unfinished jobs
        """
        for index, row in df.reset_index(drop=True).iterrows():
            try:
                self.get_job_detail(row["url"])
                print(f"Job #{index+1} retrived. Total {len(self.df)} jobs retrived.")
            except:
                print("Retrive job detail failed. Continue to next one.")
                continue

    def keep_trying(self):
        """if there are unfinished jobs, keep trying"""
        while self.if_unfinished() == True:
            unfinished_df = self.index[
                ~self.index["url"].isin(self.df["url"].to_list())
            ]
            self.trying(unfinished_df)
            time.sleep(random.uniform(1, 5))
            print("One round finished.")

    def save(self):
        self.df.to_csv("data/raw_jobs.csv", index=False)

    def save_friendly(self):
        self.df[~negative_bool(self.df["description"])].to_csv(
            "data/visa_friendly_jobs.csv", index=False
        )
