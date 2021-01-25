from manager.manager import Manager
from cleaner.judge import negative_bool

KEYWORDS = "h1b"

indeed = Manager("indeed", KEYWORDS)
indeed.build_index()
indeed.keep_trying()
print("===========================")
print("FINISHED.")
print(f"{len(indeed.df)} jobs retrived.")
indeed.save()
indeed.save_friendly()