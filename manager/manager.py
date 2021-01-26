import pandas as pd
from scraper.indeed import JobList, JobDetail
from cleaner.judge import is_negative, visa_related
import time
import random
from tqdm import tqdm


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
        self.jobs = pd.DataFrame(
            columns=["title", "company", "location", "description", "url"]
        )
        if website == "indeed":
            self.url = "https://www.indeed.com/jobs?q=" + self.KEYWORDS.replace(
                " ", "%20"
            )
        else:
            raise ValueError("Only support indeed")

        self.joblists = JobList(self.url)
        print(f"Start querying {self.KEYWORDS}.capitalize() at {self.joblists.url}")

    def any_result(self):
        if self.joblists.good_query() == True:
            return True
        else:
            print(f"Query {self.QUERY} has no result.")
            return False

    def build_index(self):
        """if local index exists, load it;
        if not, init a index with job titles and job urls, and also save to local
        """
        try:
            index = pd.read_csv(f"index_{self.KEYWORDS.replace(' ', '_')}.csv")
            print("Index exists. Load index.")
            self.pbar_jobindex = tqdm(
                total=len(index), desc=f"Index: {self.KEYWORDS.capitalize()}"
            )
            self.index = index
            self.index["error"] = 0
        except:
            print("No index found. Initializing new index.")
            index = pd.DataFrame()
            max_num = self.joblists.total_num_of_pages()
            self.pbar_jobindex = tqdm(
                total=max_num, desc=f"Index: {self.KEYWORDS.capitalize()}"
            )
            print(f"Found {max_num} pages")  # it is ok if this num is wrong

            # in case the nagination system is broken
            signal = self.joblists.current_num_of_pages()

            while self.joblists.rest_num_of_pages() >= 0:
                # print(f"Current at page #{self.joblists.current_num_of_pages()}: {self.joblists.url}")
                index = index.append(self.joblists.get_job_index(), ignore_index=True)
                self.pbar_jobindex.update(1)
                time.sleep(random.uniform(0.5, 1))
                if self.joblists.rest_num_of_pages() == 0:
                    print("last page achieved")
                    print("=============================")
                    break
                else:
                    self.joblists = JobList(self.joblists.nextpage())

                    # sometimes indeed's pagination is broken and gives infinite pages
                    if self.joblists.current_num_of_pages() < signal:
                        print("Pagination is wrong. Break here")
                        print("=============================")
                        break
                    signal = self.joblists.current_num_of_pages()

                    # print(f"remaining pages: {self.joblists.rest_num_of_pages()}")
            print(f"Total {len(index)} job urls found.")
            self.index = index.reset_index(drop=True)
            self.index.to_csv(
                f"index_{self.KEYWORDS.replace(' ', '_')}.csv", index=False
            )
            self.index["error"] = 0
        self.pbar_jobindex.close()

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
        self.jobs = self.jobs.append(output, ignore_index=True)

    def unfinished(self, retry):
        unfinished_df = self.index[~self.index["url"].isin(self.jobs["url"].to_list())]
        unfinished_df = unfinished_df[unfinished_df["error"] < retry]
        return unfinished_df

    def trying(self, df):
        """try to retrive all unfinished jobs (error < retry).
        If failed to retrive, error += 1

        Args:
            df (pd.DataFrame): df of unfinished jobs
        """
        for _, row in df.reset_index().iterrows():
            time.sleep(random.uniform(1, 3))
            try:
                self.get_job_detail(row["url"])
                # print(f"Job #{i+1} retrived. Total {len(self.jobs)} jobs retrived.")
                self.pbar_jobdetail.update(1)
            except:
                self.index.loc[row["index"], "error"] += 1
                if self.index.loc[row["index"], "error"] >= self.retry:
                    print(
                        f"MAXIUM RETRY ACHIEVED: {self.index.loc[row['index'], 'url']}"
                    )
                # print(f"\n#{self.index.loc[row['index'], 'error']} retry to retrive job detail failed.")

    def keep_trying(self, retry=10):
        """if there are unfinished jobs, keep trying"""
        self.pbar_jobdetail = tqdm(
            total=len(self.index), desc=f"Detail: {self.KEYWORDS.capitalize()}"
        )
        self.retry = retry
        while len(self.unfinished(self.retry)) > 0:
            self.trying(self.unfinished(self.retry))
            time.sleep(random.uniform(2, 5))
            print("One round finished.")
        self.pbar_jobdetail.close()

    def save_raw(self):
        self.jobs.to_csv(f"data/raw_{self.KEYWORDS.replace(' ', '_')}.csv", index=False)

    def save_neutral(self):
        self.jobs[~visa_related(self.jobs["description"])].to_csv(
            f"data/visa_neutral_{self.KEYWORDS.replace(' ', '_')}.csv", index=False
        )

    def save_friendly(self):
        visa = self.jobs[visa_related(self.jobs["description"])]
        visa[~is_negative(visa["description"])].to_csv(
            f"data/visa_friendly_{self.KEYWORDS.replace(' ', '_')}.csv", index=False
        )

    def log_error(self):
        try:
            error_log = pd.read_csv("error.csv")
        except:
            error_log = pd.DataFrame()
        new = self.index[self.index["error"] >= self.retry][["url", "title"]].to_dict()
        new["keyword"] = self.KEYWORDS
        error_log = error_log.append(new, ignore_index=True)
        error_log.to_csv("error.csv", index=False)