from typing import Dict
from prettytable import prettytable
from helpers.file_helper import transform_value_for_table
import statistics

ERR_CODE = -1000

def get_stats_per_column(data, exclude_key=["key"]) -> Dict:
    res = {}
    for key in data:
        if key in exclude_key:
            continue
        valid_values = []
        failed_cnt = 0
        not_tested_cnt = 0
        total = len(data[key])
        for val in data[key]:
            if val is None:
                not_tested_cnt += 1
                continue
            if val == ERR_CODE:
                failed_cnt += 1
                continue
            valid_values.append(val)
        if not_tested_cnt == total:
            res[key] = {"median": "-", "avg": "-"}
        elif failed_cnt == total or failed_cnt + not_tested_cnt == total:
            res[key] = {"median": "ERR", "avg": "ERR"}
        else:
            avg = sum(valid_values) / (total - (failed_cnt + not_tested_cnt))
            median = statistics.median(valid_values)
            res[key] = {"median": round(median, 2), "avg": round(avg, 2)}
    return res


def build_rows_from_stats(data):
    avg_row = ["Average"]
    median_row = ["median"]
    for key in ["rest", "websocket"]:
        avg_row.append(data[f"wer_{key}"]["avg"])
        median_row.append(data[f"wer_{key}"]["median"])
        avg_row.append(data[f"duration_{key}"]["avg"])
        median_row.append(data[f"duration_{key}"]["median"])
    return [avg_row, median_row]


def render_table(data: dict):
    table = prettytable.PrettyTable()
    table.field_names = [
        "File",
        "Rest WER",
        "Rest Duration",
        "WS WER",
        "WS Duration",
    ]
    for i in range(len(data["key"])):
        row = [
            data["key"][i],
            transform_value_for_table(data["wer_rest"][i]),
            transform_value_for_table(data["duration_rest"][i]),
            transform_value_for_table(data["wer_websocket"][i]),
            transform_value_for_table(data["duration_websocket"][i]),
        ]
        if i == len(data["key"]) - 1:
            table.add_row(row, divider=True)
            continue
        table.add_row(row)

    table.add_rows(build_rows_from_stats(get_stats_per_column(data)))
    print(table)
