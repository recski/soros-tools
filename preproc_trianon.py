import csv
import json
import sys

from tqdm import tqdm

from emtsv import run_emtsv_all, run_emtsv_tok


def parse_row(row):
    (
        doc_id_x,
        doc_id,
        doc_type,
        title,
        author,
        author_id,
        content,
        date_created,
        date_added,
        context,
        url,
        domain,
        sentiment,
        sent_points,
        comments,
        views,
        shares,
        wow,
        love,
        like,
        haha,
        sad,
        angry,
        thankful,
        fans,
        url_orig,
        content_orig,
        domain_category,
    ) = row  # noqa
    doc = {
        "doc_id": doc_id,
        "doc_type": doc_type,
        "title": title,
        "author": {"id": author_id, "name": author},
        "content": content,
        "date_created": date_created,
        "date_added": date_added,
        "context": context,
        "url": url,
        "domain": domain,
        "domain_category": domain_category,
    }
    return doc


def run_emtsv(text):
    if len(text) > 100000:
        sys.stderr.write("skipping long sen ({} chars)\n".format(len(text)))
        return None
    sens = run_emtsv_tok(text)
    return [{"text": sen["text"], "ana": run_emtsv_all(sen["text"])} for sen in sens]


def main():
    for i, row in tqdm(enumerate(csv.reader(sys.stdin, delimiter=";", quotechar='"'))):
        if i == 0 and row[0] == "X":
            continue
        doc = parse_row(row)
        doc["content"] = {"text": doc["content"], "sens": run_emtsv(doc["content"])}
        print(json.dumps(doc))


if __name__ == "__main__":
    main()
