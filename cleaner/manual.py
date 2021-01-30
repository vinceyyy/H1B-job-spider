# %%
import pandas as pd
from judge import *
import os


# manual fix
(_, _, filenames) = next(os.walk("../data"))
filenames = [filename for filename in filenames if filename.endswith(".csv")]
for filename in filenames:
    df = pd.read_csv(f"../data/{filename}")
    print(filename, df.columns)
    # neutral
    df[~visa_related(df["description"])].to_csv(
        f"../data/{filename.replace('raw', 'visa_neutral')}", index=False
    )
    # friendly
    visa = df[visa_related(df["description"])]
    visa[~is_negative(visa["description"])].to_csv(
        f"../data/{filename.replace('raw', 'visa_friendly')}",
        index=False,
    )

# %%
