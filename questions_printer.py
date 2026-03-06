#!/usr/bin/env python3
import csv
import json
import re
import sys
from pathlib import Path


def excel_col(n: int) -> str:
    ##Example: 1 -> A, 27 -> AA

    result = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


def looks_like_importid_row(row):
    """
    Detect Qualtrics-style import row such as:
    {"ImportId":"QID2011"}
    """
    nonempty = [cell.strip() for cell in row if cell.strip()]
    if not nonempty:
        return False

    hits = 0
    for cell in nonempty:
        if '"ImportId"' in cell or "ImportId" in cell:
            hits += 1
    return hits >= max(1, len(nonempty) // 2)


def is_question_column(header: str) -> bool:
    """
    header starts with Q.
    """
    return bool(re.match(r"^Q", header.strip(), re.IGNORECASE))
def safe_get(row, idx):
    return row[idx] if idx < len(row) else ""


def main():
    if len(sys.argv) < 2:
        print("ew")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) >= 3 else None
    with input_file.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if len(rows) < 2:
        print("CSV too small.")
        sys.exit(1)

    header_row_num = 1
    question_row_num = 2
    import_row_num = 3 if len(rows) >= 3 and looks_like_importid_row(rows[2]) else None
    data_start_row_num = 4 if import_row_num else 3
    headers = rows[0]
    question_texts = rows[1]
    results = []

    for col_idx, header in enumerate(headers):
        if not is_question_column(header):
            continue

        question_text = safe_get(question_texts, col_idx).strip()
        if not question_text:
            question_text = "(no questions)"

        nonempty_answer_rows = []
        for row_num in range(data_start_row_num, len(rows) + 1):
            value = safe_get(rows[row_num - 1], col_idx).strip()
            if value != "":
                nonempty_answer_rows.append(row_num)

        result = {
            "machine_header": header,
            "question_text": question_text,
            "column_number": col_idx + 1,
            "column_letter": excel_col(col_idx + 1),
            "question_text_row": question_row_num,
            "data_start_row": data_start_row_num,
            "nonempty_answer_count": len(nonempty_answer_rows),
            "nonempty_answer_rows": nonempty_answer_rows,
            "answer_range": f"R{data_start_row_num}C{col_idx+1}:R{len(rows)}C{col_idx+1}",
        }
        results.append(result)

    # Readable output
    # print(f"Input file: {input_file}")
    print(f"Header row: {header_row_num}")
    print(f"Question text row: {question_row_num}")
    print(f"Import/meta row: {import_row_num if import_row_num else 'not detected'}")
    print()
    print(f"Found {len(results)} survey question columns.")
    
    print("-" * 10)

    for i, item in enumerate(results, start=1):
        print(f"{i}. {item['machine_header']}")
        print(f"   Question: {item['question_text']}")
        print(f"   Column: {item['column_number']} ({item['column_letter']})")
        print(f"   Question cell: row {item['question_text_row']}, col {item['column_number']}")
        print(f"   Answers range: {item['answer_range']}")
        print(f"   Rows with answers ({item['nonempty_answer_count']}): {item['nonempty_answer_rows']}")
        print("-" * 100)

    # Optional CSV export
    if output_file:
        with output_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "machine_header",
                "question_text",
                "column_number",
                "column_letter",
                "question_text_row",
                "data_start_row",
                "nonempty_answer_count",
                "nonempty_answer_rows",
                "answer_range",
            ])
            for item in results:
                writer.writerow([
                    item["machine_header"],
                    item["question_text"],
                    item["column_number"],
                    item["column_letter"],
                    item["question_text_row"],
                    item["data_start_row"],
                    item["nonempty_answer_count"],
                    json.dumps(item["nonempty_answer_rows"]),
                    item["answer_range"],
                ])

        print(f"\nSaved parsed question list to: {output_file}")


if __name__ == "__main__":
    main()