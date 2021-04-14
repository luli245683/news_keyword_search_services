__copyright__ = "Copyright (c) 2021 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import os

import click
from jina.flow import Flow


MAX_DOCS = int(os.environ.get("JINA_MAX_DOCS", 500))


def config(pretrained_model):
    os.environ["JINA_DATA_FILE"] = os.environ.get(
        "JINA_DATA_FILE", "data/news_titles.txt"
    )
    
    
    if pretrained_model=='roberta':
        os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(56789))
        os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "roberta")
    else:
        os.environ["JINA_PORT"] = os.environ.get("JINA_PORT", str(45678))
        os.environ["JINA_WORKSPACE"] = os.environ.get("JINA_WORKSPACE", "ckip")


def print_topk(resp, sentence):
    for d in resp.search.docs:
        print(f"Ta-Dah🔮, here are what we found for: {sentence}")
        for idx, match in enumerate(d.matches):

            score = match.score.value
            if score < 0.0:
                continue
            print(f'> {idx:>2d}({score:.2f}). {match.text}')


def index(num_docs, pretrained_model):
    if pretrained_model=='roberta':
        f = Flow().load_config("flows/index_roberta.yml")
    else:
        f = Flow().load_config("flows/index.yml")

    with f:
        data_path = os.path.join(os.path.dirname(__file__), os.environ.get('JINA_DATA_FILE', None))
        f.index_lines(filepath=data_path, batch_size=16, read_mode='r', size=num_docs)


def query(top_k):
    f = Flow().load_config("flows/query.yml")
    with f:
        while True:
            text = input("please type a sentence: ")
            if not text:
                break

            def ppr(x):
                print_topk(x, text)

            f.search_lines(lines=[text, ], line_format='text', on_done=ppr, top_k=top_k)


def query_restful():
    f = Flow().load_config("flows/query.yml")
    f.use_rest_gateway()
    with f:
        f.block()


def dryrun():
    f = Flow().load_config("flows/index.yml")
    with f:
        f.dry_run()


@click.command()
@click.option(
    "--task",
    "-t",
    type=click.Choice(
        ["index", "query", "query_restful", "dryrun"], case_sensitive=False
    ),
)
@click.option("--num_docs", "-n", default=MAX_DOCS)
@click.option("--top_k", "-k", default=5)
@click.option("--pretrained_model", "-m", default='ckip')
def main(task, num_docs, top_k, pretrained_model):
    config(pretrained_model)
    workspace = os.environ["JINA_WORKSPACE"]
    if task == "index":
        if os.path.exists(workspace):
            print(f'\n +----------------------------------------------------------------------------------+ \
                    \n |                                   🤖🤖🤖                                         | \
                    \n | The directory {workspace} already exists. Please remove it before indexing again.  | \
                    \n |                                   🤖🤖🤖                                         | \
                    \n +----------------------------------------------------------------------------------+')
        index(num_docs, pretrained_model)
    if task == "query":
        if not os.path.exists(workspace):
            print(f"The directory {workspace} does not exist. Please index first via `python app.py -t index`")
        query(top_k)
    if task == "query_restful":
        if not os.path.exists(workspace):
            print(f"The directory {workspace} does not exist. Please index first via `python app.py -t index`")
        query_restful()
    if task == "dryrun":
        dryrun()


if __name__ == "__main__":
    main()
