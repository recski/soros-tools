import json
import sys

import networkx as nx
from xpotato.dataset.dataset import Dataset


def get_graph_from_ana(sen):
    G = nx.DiGraph()
    root_id = 0
    for tok in sen['toks']:
        tok_id = int(tok['id'])
        head_id = int(tok['head'])
        G.add_node(tok_id, name=tok["lemma"])

        if tok["deprel"] == "root":
            root_id = tok_id
            G.add_node(head_id, name="root")
        G.add_edge(head_id, tok_id)
        G[head_id][tok_id].update(
            {'color': tok["deprel"]})

    return G, root_id


def gen_graphs_from_json(stream):
    for line in stream:
        doc = json.loads(line)
        # doc_id = doc['doc_id']
        for sen in doc['content']['soros_sens']:
            text = sen['text']
            graph, _ = get_graph_from_ana(sen['ana'][0])
            for ana_sen in sen['ana'][1:]:
                sgraph, _ = get_graph_from_ana(ana_sen)
                graph = nx.compose(graph, sgraph)
            yield text, graph


def main():
    dataset_fn = sys.argv[1]
    with open(dataset_fn, 'w') as _:
        pass  # test if writable

    texts, graphs = [], []
    for text, graph in gen_graphs_from_json(sys.stdin):
        texts.append((text, ''))
        graphs.append(graph)

    dataset = Dataset(texts, label_vocab={}, lang='hu')
    dataset.set_graphs(graphs)
    df = dataset.to_dataframe()
    df.to_pickle(dataset_fn)


if __name__ == "__main__":
    main()
