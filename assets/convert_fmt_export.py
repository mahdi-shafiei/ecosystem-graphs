import pandas as pd
from typing import Dict, Tuple, Callable
import yaml
from yaml import Loader, Dumper
from datetime import datetime


def wrap_return_value(return_key="value"):
    def decorator(fn):
        def helper(*args, **kwargs):
            return {return_key: fn(*args, **kwargs)}

        return helper

    return decorator


def datetime_converter(date_string) -> datetime:
    """
    >>> datetime_converter('2022/05/01')
    datetime.date(2022, 5, 1)
    """
    return datetime.strptime(date_string, "%Y/%m/%d").date()


def modality_converter(languages) -> str:
    languages = languages.split(", ")
    nat_langs = sorted([l for l in languages if l != "Code | 1 0"])
    return f"Text ({', '.join(nat_langs)})" + (
        (" and Code") if "Code | 1 0" in languages else ""
    )


def size_converter(size, llm_type) -> str:
    return f"{int(size)}B parameters" + (
        " (sparse" if "sparse" in llm_type else " (dense" + " model)"
    )


def fmt_to_eco_entry(fmt_entry: pd.Series) -> str:
    if fmt_entry['_HIDEME'] == True:
        return {}

    ret = {}

    # Hard coded fields
    ret["type"] = "model"

    # Fields named differently but same value
    ret["name"] = fmt_entry["Name"]
    ret["organization"] = fmt_entry["Organization"]
    ret["training_hardware"] = fmt_entry["Cluster"]
    ret["url"] = fmt_entry["Paper / announcement link"]

    # Fields requiring conversion
    ret["modality"] = modality_converter(fmt_entry["Languages"])
    ret["size"] = size_converter(fmt_entry["Params (B; Max)"], fmt_entry["Type"])

    # Nested fields
    created_date = {}
    created_date["value"] = datetime_converter(fmt_entry["Announced date"])
    created_date["explanation"] = ""
    ret["created_date"] = created_date

    license = {}
    license["value"] = fmt_entry["Model License"]
    license["explanation"] = fmt_entry["Model release comments"]
    ret["license"] = license

    # Reorder keys (suboptimal performance, better code legibility)
    eco_schema = [
        "type",
        "name",
        "organization",
        "description",
        "created_date",
        "url",
        "model_card",
        "modality",
        "size",
        "analysis",
        "dependencies",
        "training_emissions",
        "training_time",
        "training_hardware",
        "quality_control",
        "access",
        "license",
        "intended_uses",
        "prohibited_uses",
        "monitoring",
        "feedback",
    ]
    final = {k: ret.get(k, "") for k in eco_schema}

    return yaml.dump(final, sort_keys=False)


def main():
    FMT = pd.read_csv("FMT_LLM_dump_20221104.csv")
    for _, row in FMT.iterrows():
        print(fmt_to_eco_entry(row))
    # print(FMT.apply(fmt_to_eco_entry, axis=1))


if __name__ == "__main__":
    main()
