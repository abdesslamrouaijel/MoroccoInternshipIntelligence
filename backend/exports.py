import csv
import json
from pathlib import Path

from config.settings import EXPORT_DIR

FIELDS = ["company_name", "title", "region", "location", "source", "published_at", "skills", "score", "url", "status"]


def export_opportunities(rows, fmt, output_dir=EXPORT_DIR):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"opportunities.{fmt}"
    records = [{field: getattr(row, field, "") for field in FIELDS} for row in rows]
    if fmt == "json":
        path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    elif fmt == "csv":
        with path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(records)
    elif fmt == "xlsx":
        from openpyxl import Workbook
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Opportunities"
        sheet.append(FIELDS)
        for record in records:
            sheet.append([record[field] for field in FIELDS])
        workbook.save(path)
    elif fmt == "pdf":
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        data = [FIELDS] + [[str(record[field]) for field in FIELDS] for record in records]
        doc = SimpleDocTemplate(str(path), pagesize=landscape(letter))
        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#183153")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
        ]))
        doc.build([table])
    else:
        raise ValueError(f"Unsupported export format: {fmt}")
    return path
