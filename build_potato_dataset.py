import json
import sys

import networkx as nx
from tqdm import tqdm
from xpotato.dataset.dataset import Dataset
from xpotato.graph_extractor.graph import PotatoGraph
from tuw_nlp.common.vocabulary import Vocabulary


TRIANON_LABEL_MAP = {
    "nem kormánypárti": "NON_GOV",
    "kormánypárti": "GOV",
    "szélsőjobboldali": "FAR_RIGHT",
}


def get_graph_from_ana(sen):
    G = nx.DiGraph()
    root_id = None
    for tok in sen["toks"]:
        tok_id = int(tok["id"])
        head_id = int(tok["head"])
        deprel = tok["deprel"].lower()
        G.add_node(tok_id, name=tok["lemma"])

        if deprel == "root":
            root_id = tok_id
            G.add_node(head_id, name="root")
        G.add_edge(head_id, tok_id)
        G[head_id][tok_id].update({"color": deprel})

    if root_id is None:
        G.add_node(0, name="root")

    return G, root_id


def get_text_ana_label_from_json(doc, data_type):
    if data_type == "soros":
        yield from get_text_ana_label_soros(doc)
    elif data_type == "trianon":
        yield from get_text_ana_label_trianon(doc)


def get_text_ana_label_trianon(doc):
    for sen in doc["content"]["sens"]:
        yield sen["ana"]["text"], sen["ana"]["ana"], TRIANON_LABEL_MAP[
            doc["domain_category"]
        ]


def get_text_ana_label_soros(doc):
    if "soros_sens" not in doc["content"]:
        return
    for sen in doc["content"]["soros_sens"]:
        yield sen["text"], sen["ana"], "???"


def gen_data_from_json(stream, data_type):
    for line in tqdm(stream):
        doc = json.loads(line)
        for text, ana, label in get_text_ana_label_from_json(doc, data_type):
            # doc_id = doc['doc_id']
            text = text.replace("\n", " ").replace("\r", "")
            graph, _ = get_graph_from_ana(ana[0])
            for ana_sen in ana[1:]:
                if not ana_sen["toks"]:
                    continue
                sgraph, _ = get_graph_from_ana(ana_sen)
                graph = nx.compose(graph, sgraph)

            for node, data in graph.nodes(data=True):
                if "name" not in data:
                    print(graph.nodes(data=True))
                    print(ana[0])
                    sys.exit(-1)

            yield text, PotatoGraph(graph), label


def main():
    dataset_fn = sys.argv[1]
    data_type = sys.argv[2]
    assert data_type in ("soros", "trianon")
    with open(dataset_fn, "w") as _:
        pass  # test if writable

    texts, graphs = [], []
    label_vocab = Vocabulary()
    for text, graph, label in gen_data_from_json(sys.stdin, data_type):
        texts.append((text, label))
        label_vocab.add(label)
        graphs.append(graph)

    dataset = Dataset(texts, label_vocab=label_vocab.word_to_id, lang="hu")
    dataset.set_graphs(graphs)
    dataset.save_dataset(dataset_fn)


if __name__ == "__main__":
    main()
