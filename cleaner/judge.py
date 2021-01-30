#%%
import pandas as pd
import re
import os

# %%
def visa_sentences(series: pd.Series) -> pd.Series:
    """output only visa related senteces for manually checking

    Args:
        series (pd.Series): column of description

    Returns:
        series (pd.Series): column of visa related senteces
    """
    pattern = re.compile(
        "(\n.*?(?:[ -/]visa[ -/]|[ -/]h-?1b[ -/]|[ -/]opt[ -/]).*?\n)", re.IGNORECASE
    )
    visa_sentences = series.str.extractall(pattern)[0].str.strip()
    return visa_sentences


def visa_related(series: pd.Series) -> pd.Series:
    """check if job is visa related

    Returns:
        series (pd.Series): boolean series, True == related
    """
    visas = [
        "h-?1b",
        "[^\w]visas?[^\w]",
        "[^\w]opt[^\w]",
        "[^\w]cpt[^\w]",
    ]
    related = series.str.contains("|".join(visas), flags=re.IGNORECASE)
    return related


def is_negative(series: pd.Series) -> pd.Series:
    """check if OPT/H1B acceptance is negative

    Returns:
        series (pd.Series): boolean series, True == negative
    """
    NEGATIVE_LIST_FILE = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "negative.txt")
    )
    NEGATIVE_LIST = []
    with open(NEGATIVE_LIST_FILE) as file:
        for line in file:
            li = line.strip()
            if li and not li.startswith("#"):
                NEGATIVE_LIST.append(
                    re.sub("h1b", "(h1b|h-1b)", line.rstrip("\n"), flags=re.IGNORECASE)
                )
    negative = series.str.contains("|".join(NEGATIVE_LIST), flags=re.IGNORECASE)
    return negative
