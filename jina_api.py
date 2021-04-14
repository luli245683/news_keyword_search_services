from jina.parsers import set_client_cli_parser
from jina.clients import Client
from jina import Document

def send_query_request(host, port, query):
    print(f'search request sent to {host}:{port}')
    args = set_client_cli_parser().parse_args(
        ['--host', host, '--port-expose', str(port)])
    grpc_client = Client(args)
    grpc_client.search(
        [Document(text=query), ], on_done=print)
    
if __name__ == '__main__':
    host_ip = 'http://localhost'
    flow_port = '45678'
    send_query_request(host_ip, flow_port, "台積電")