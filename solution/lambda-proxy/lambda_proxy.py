import argparse
import json
import requests
import signal
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

class ApiProxy:
    def start_server(self, hostname, internal_port, external_port):
        class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def do_GET(self):
                self._handle_request("GET", requests.get)

            def do_DELETE(self):
                self._handle_request("DELETE", requests.delete)

            def do_POST(self):
                self._handle_request("POST", requests.post)

            def do_PUT(self):
                self._handle_request("PUT", requests.put)

            def do_PATCH(self):
                self._handle_request("PATCH", requests.patch)

            def _handle_request(self, method, requests_func):
                url = f"http://{hostname}:{internal_port}/2015-03-31/functions/function/invocations"
                path = urllib.parse.urlparse(self.path)
                
                headers = dict(self.headers)
                body = self.rfile.read(int(self.headers["content-length"])) if "content-length" in headers else None

                query_params = urllib.parse.parse_qs(path.query)
                for i in query_params:
                    query_params[i] = ",".join(query_params[i])

                cookies = []  # TODO: handle this

                # See https://docs.aws.amazon.com/lambda/latest/dg/urls-invocation.html for payload structure
                data = {
                    "version": "2.0",
                    "rawPath": path.path,
                    "rawQueryString": path.query,
                    "headers": headers,
                    "cookies": cookies,
                    "queryStringParameters": query_params,
                    "body": None,  # TODO: handle this
                    "requestContext": {
                        "http": {
                            "method": method,
                            "path": path,
                            "protocol": "HTTP/1.1",
                            "userAgent": headers.get("User-Agent", ""),
                        },
                    },
                    "isBase64Encoded": False,  # TODO: handle this
                }

                resp = requests.post(url, headers=headers, data=json.dumps(data))

                self.send_response(resp.status_code)
                for key in resp.headers:
                    self.send_header(key, resp.headers[key])
                self.end_headers()
                self.wfile.write(resp.content)

        server_address = ('', external_port)
        self.httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)
        self.httpd.serve_forever()


def exit_now(signum, frame):
    sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="lambda-proxy",
        description="Proxy server to convert standard HTTP requests to Lambda POST requests.",
    )
    parser.add_argument("hostname", help="Host name where the Lambda is running.")
    parser.add_argument("internal_port", help="The port that the Lambda is running on.", type=int)
    parser.add_argument("external_port", help="The port to expose the proxy on.", type=int)
    args = parser.parse_args()

    proxy = ApiProxy()
    signal.signal(signal.SIGTERM, exit_now)
    proxy.start_server(args.hostname, args.internal_port, args.external_port)
