import csv
import json
import sys

from tqdm import tqdm

from emtsv import run_emtsv_all, run_emtsv_tok


def parse_row(row):
    (
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
        month,
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
        "month": month,
    }
    return doc


def keep_sen(sen):
    if len(sen["toks"]) > 100:
        return False

    for tok in sen["toks"]:
        if tok.lower().startswith("soros"):
            return True
    return False


def filter_sens(sens):
    return [sen for sen in sens if keep_sen(sen)]


def run_emtsv(text):
    content = {"text": text}
    if len(text) > 5000:
        sys.stderr.write("skipping long sen ({} chars)\n".format(len(text)))
        return content
    sens = run_emtsv_tok(text)
    content["sens"] = sens
    soros_sens = filter_sens(sens)
    # sys.stderr.write('analyzing {} soros_sens from {} sens\n'.format(
    #    len(soros_sens), len(sens)))
    content["soros_sens"] = [run_emtsv_all(sen["text"]) for sen in soros_sens]

    return content


def main():
    for i, row in tqdm(enumerate(csv.reader(sys.stdin, delimiter=";", quotechar='"'))):
        if i == 0 and row[0] == "id":
            continue
        doc = parse_row(row)
        doc["content"] = run_emtsv(doc["content"])
        doc["context"] = run_emtsv(doc["context"])
        print(json.dumps(doc))


if __name__ == "__main__":
    main()
