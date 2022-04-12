import requests

EMTSV_URL = 'http://127.0.0.1:5000/tok/spell/morph/pos/conv-morph/dep/chunk/ner'  # noqa
# EMTSV_URL = 'http://127.0.0.1:5000/tok-dep'  # noqa
EMTSV_URL_TOK = 'http://127.0.0.1:5000/tok'  # noqa
# EMTSV_URL = 'http://127.0.0.1:5000/tok/spell/morph/pos/conv-morph/dep'  # noqa


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
        wsafter = eval(wsafter)
        sens[-1]['toks'].append(tok)
        sens[-1]['text'] += tok + wsafter

    return sens


def run_emtsv_tok(text):
    r = requests.post(EMTSV_URL_TOK, data={'text': text})
    sens = parse_emtsv_toks(r.text)
    return sens
