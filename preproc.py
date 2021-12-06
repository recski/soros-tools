import csv
import json
import sys

import requests
from tqdm import tqdm

EMTSV_URL = 'http://127.0.0.1:5000/tok/spell/morph/pos/conv-morph/dep/chunk/ner'  # noqa
EMTSV_URL_TOK = 'http://127.0.0.1:5000/tok'  # noqa
# EMTSV_URL = 'http://127.0.0.1:5000/tok/spell/morph/pos/conv-morph/dep'  # noqa


def parse_row(row):
    doc_id, doc_type, title, author, author_id, content, date_created, date_added, context, url, domain, month = row  # noqa
    doc = {
        "doc_id": doc_id,
        "doc_type": doc_type,
        "title": title,
        "author": {
            "id": author_id,
            "name": author},
        "content": content,
        "date_created": date_created,
        "date_added": date_added,
        "context": context,
        "url": url,
        "domain": domain,
        "month": month
    }
    return doc


def parse_emtsv_output(raw_output):
    sens = [{"sen_id": 0, "toks": []}]
    for i, raw_line in enumerate(raw_output.split('\n')):
        if i == 0:
            continue
        if not raw_line:
            sens.append({"sen_id": sens[-1]['sen_id'] + 1, "toks": []})
            continue
        fields = raw_line.split('\t')
        assert len(fields) == 14, (fields, raw_line)
        # assert len(fields) == 12, (fields, raw_line)
        word, wsafter, spell, hunspell_anas, anas, lemma, xpostag, upostag, feats, xid, deprel, head, np_bio, ner_bio = fields  # noqa
        # word, wsafter, spell, hunspell_anas, anas, lemma, xpostag, upostag, feats, xid, deprel, head = fields  # noqa
        sens[-1]["toks"].append({
            "id": xid,
            "text": word,
            "lemma": lemma,
            "upos": upostag,
            "xpos": xpostag,
            "feats": feats,
            "head": head,
            "deprel": deprel,
            "misc": f"wsafter={wsafter}|np={np_bio}",
            "ner": ner_bio,
            "anas": eval(anas),
            "hunspell_anas": eval(hunspell_anas)})

    if not sens[-1]['toks']:
        sens = sens[:-1]

    return sens


def run_emtsv_all(text):
    r = requests.post(EMTSV_URL, data={'text': text})
    ana = parse_emtsv_output(r.text)
    return {
        "text": text,
        "ana": ana}


def parse_emtsv_toks(raw_output):
    sens = [{'toks': [], 'text': ''}]
    for i, line in enumerate(raw_output.split('\n')):
        if i == 0:
            continue
        if line == '':
            sens.append({'toks': [], 'text': ''})
            continue
        tok, wsafter = line.split('\t')
        sens[-1]['toks'].append(tok)
        sens[-1]['text'] += tok + wsafter

    return sens


def run_emtsv_tok(text):
    r = requests.post(EMTSV_URL_TOK, data={'text': text})
    sens = parse_emtsv_toks(r.text)
    return sens


def keep_sen(sen):
    if len(sen['toks']) > 100:
        return False

    for tok in sen['toks']:
        if tok.lower().startswith('soros'):
            return True
    return False


def filter_sens(sens):
    return [sen for sen in sens if keep_sen(sen)]


def run_emtsv(text):
    content = {'text': text}
    if len(text) > 5000:
        sys.stderr.write('skipping long sen ({} chars)\n'.format(len(text)))
        return content
    sens = run_emtsv_tok(text)
    content['sens'] = sens
    soros_sens = filter_sens(sens)
    # sys.stderr.write('analyzing {} soros_sens from {} sens\n'.format(
    #    len(soros_sens), len(sens)))
    content['soros_sens'] = [run_emtsv_all(sen['text']) for sen in soros_sens]

    return content


def main():
    for i, row in tqdm(enumerate(
            csv.reader(sys.stdin, delimiter=";", quotechar='"'))):
        if i == 0 and row[0] == 'id':
            continue
        doc = parse_row(row)
        doc['content'] = run_emtsv(doc['content'])
        doc['context'] = run_emtsv(doc['context'])
        print(json.dumps(doc))


if __name__ == "__main__":
    main()
