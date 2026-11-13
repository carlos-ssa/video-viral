"""Planeja uma consulta Google Trends e importa CSV oficial de interesse ao longo do tempo.

Uso: python scripts/trends.py <projeto> --terms "barbearia" "salao de beleza"
     --geo BR --timeframe "today 3-m" --property youtube [--csv multiTimeline.csv]

Sem --csv, só mostra a URL. Não faz scraping, não baixa dados nem exige chave de API.
"""
import argparse
import csv
from datetime import date, datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import urlencode

from _common import file_sha256, load_manifest, project_dir, save_manifest

DATE_HEADERS = {"day", "week", "month", "hour", "date", "time", "dia", "semana", "mês", "mes", "hora", "data"}


def explore_url(terms, geo="BR", timeframe="today 3-m", property_="youtube", category=0):
    return "https://trends.google.com/trends/explore?" + urlencode(
        {"q": ",".join(terms), "geo": geo, "date": timeframe,
         "gprop": "" if property_ == "web" else property_, "cat": category, "hl": "pt-BR"})


def parse_interest_csv(text):
    """Só série temporal do site (0–100); não interpreta CSV de regiões/consultas nem dados da API."""
    selected = None
    for delimiter in (",", ";", "\t"):
        try:
            rows = list(csv.reader(io.StringIO(text.lstrip("\ufeff")), delimiter=delimiter, strict=True))
        except csv.Error:
            continue
        for index, row in enumerate(rows):
            if len(row) >= 2 and row[0].strip().casefold() in DATE_HEADERS:
                selected = rows[index:]
                break
        if selected is not None:
            break
    if not selected:
        raise ValueError("CSV sem cabeçalho de série temporal (Dia/Week/Month); exporte Interesse ao longo do tempo.")
    header = [cell.strip() for cell in selected[0]]
    labels = header[1:]
    if any(not label for label in labels) or len(set(labels)) != len(labels):
        raise ValueError("Séries vazias ou duplicadas no CSV.")
    points = []
    for line, row in enumerate(selected[1:], 2):
        if not row or not any(cell.strip() for cell in row):
            continue
        if len(row) != len(header):
            raise ValueError(f"Linha de dados {line}: número de campos inválido.")
        period = row[0].strip()
        try:
            date.fromisoformat(period + "-01" if re.fullmatch(r"\d{4}-\d{2}", period) else period[:10])
        except ValueError as exc:
            raise ValueError(f"Linha de dados {line}: período inválido.") from exc
        values = {}
        for label, raw in zip(labels, row[1:]):
            raw = raw.strip()
            if raw in ("<1", "< 1", ""):
                values[label] = {"index": None, "raw": raw, "below_one": bool(raw)}
            elif re.fullmatch(r"\d{1,3}", raw) and int(raw) <= 100:
                values[label] = {"index": int(raw), "raw": raw, "below_one": False}
            else:
                raise ValueError(f"Linha de dados {line}: índice inválido {raw!r}; esperado 0–100 ou <1.")
        points.append({"period": period, "values": values})
    if not points:
        raise ValueError("CSV sem observações.")
    return {"series": labels, "points": points}


def import_csv(proj, path, terms, geo, timeframe, property_, category=0):
    data = parse_interest_csv(path.read_text(encoding="utf-8-sig"))
    if len(terms) != len(data["series"]) or any(
            label.casefold() != term.casefold() and not label.casefold().startswith(term.casefold() + ":")
            for term, label in zip(terms, data["series"])):
        raise ValueError("Os termos e sua ordem não correspondem ao CSV; use os nomes exibidos na exportação.")
    digest = file_sha256(path)
    source = proj / "research" / "trends" / f"{digest}.csv"
    url = explore_url(terms, geo, timeframe, property_, category)
    context = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    record = source.with_name(f"{digest}-{context}.json")
    m = load_manifest(proj)
    if not isinstance(m.get("research", {}), dict):
        raise ValueError("research precisa ser um objeto no manifesto.")
    observation = {"source": "Google Trends", "access": "website_csv", "scale": "relative_index_0_100",
                   "collected_at": datetime.now(timezone.utc).isoformat(), "source_sha256": digest,
                   "terms": terms, "geo": geo, "timeframe": timeframe, "property": property_, "category": category,
                   "source_csv": source.relative_to(proj).as_posix(),
                   "filters_provenance": "declarados na importação; conferir com a configuração da exportação",
                   "url": url, **data,
                   "limitations": ["Interesse de busca relativo; não é volume absoluto nem retenção/conversão.",
                                   "0 pode indicar dados insuficientes; <1 é preservado sem imputação.",
                                   "Não comparar índices de exportações com escalas/filtros diferentes."]}
    # Validate everything before writing evidence or updating the manifest.
    source.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        source.write_bytes(path.read_bytes())
    temporary = record.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(observation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(record)
    m.setdefault("research", {})["google_trends"] = {"path": record.relative_to(proj).as_posix(),
                                                     "source_sha256": digest, "url": observation["url"]}
    save_manifest(proj, m)
    return record


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project")
    ap.add_argument("--terms", nargs="+", required=True)
    ap.add_argument("--geo", default="BR")
    ap.add_argument("--timeframe", default="today 3-m")
    ap.add_argument("--property", choices=["web", "youtube"], default="youtube")
    ap.add_argument("--category", type=int, default=0, help="ID da categoria no Trends; 0 = todas")
    ap.add_argument("--csv", type=Path)
    args = ap.parse_args()
    proj = project_dir(args.project)
    terms = [term.strip() for term in args.terms]
    if args.category < 0:
        ap.error("Categoria precisa ser um ID não negativo.")
    if any(not term for term in terms):
        ap.error("Termos não podem ficar vazios.")
    print(explore_url(terms, args.geo, args.timeframe, args.property, args.category))
    if args.csv:
        try:
            print(import_csv(proj, args.csv, terms, args.geo, args.timeframe, args.property, args.category))
        except (OSError, ValueError) as exc:
            ap.error(str(exc))


if __name__ == "__main__":
    main()
