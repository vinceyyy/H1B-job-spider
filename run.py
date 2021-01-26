from manager.manager import Manager

KEYWORDS_LIST = [
    "growth marketing",
    "marketing analyst",
    "multicultural marketing",
    "google analytics",
    "chinese marketing",
    "chinese analyst",
]

for keyword in [keyword for keyword in KEYWORDS_LIST]:
    indeed = Manager("indeed", keyword)
    if indeed.any_result() == True:
        indeed.build_index()
        indeed.keep_trying()
        indeed.pbar.close()
    indeed.log_error()
    print("===========================")
    print("FINISHED.")
    print(f"{len(indeed.df)} jobs retrived.")
    indeed.save_raw()
    indeed.save_neutral()
    indeed.save_friendly()
    print("============")
    print(f"{keyword} FILE SAVED.")
    print("============")