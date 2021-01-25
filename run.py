from manager.manager import Manager
from cleaner.judge import negative_bool

KEYWORDS_LIST = ["google analytics", "chinese marketing", "chinese analyst"]

for keyword in [keyword for keyword in KEYWORDS_LIST]:
    indeed = Manager("indeed", keyword)
    if indeed.any_result() == True:
        indeed.build_index()
        indeed.keep_trying()
    indeed.log_error()
    print("===========================")
    print("FINISHED.")
    print(f"{len(indeed.df)} jobs retrived.")
    indeed.save()
    indeed.save_friendly()
    print("============")
    print(f"{keyword} FILE SAVED.")
    print("============")