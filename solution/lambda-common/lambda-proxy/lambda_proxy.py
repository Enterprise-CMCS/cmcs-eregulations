import argparse
import json
import threading
from queue import Queue
import signal
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests


class ApiProxy:
    def start_server(self, hostname, internal_port, external_port, enable_async):
        queue = Queue()

        def process_requests():
            while True:
                request = queue.get()
                try:
                    requests.post(request["url"], headers=request["headers"], data=request["data"])
                except Exception as e:
                    print(f"Error processing async request: {str(e)}")
                queue.task_done()

        class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"

            def do_GET(self):
                self._handle_request("GET")

            def do_DELETE(self):
                self._handle_request("DELETE")

            def do_POST(self):
                self._handle_request("POST")

            def do_PUT(self):
                self._handle_request("PUT")

            def do_PATCH(self):
                self._handle_request("PATCH")

            def _send_response(self, status_code, headers, body):
                self.send_response(status_code)
                for key in headers:
                    self.send_header(key, headers[key])
                self.end_headers()
                body = body.encode() if not isinstance(body, bytes) else body
                self.wfile.write(body)

            def _handle_request(self, method):
                url = f"http://{hostname}:{internal_port}/2015-03-31/functions/function/invocations"
                path = urllib.parse.urlparse(self.path)

                headers = dict(self.headers)
                body = self.rfile.read(int(self.headers["Content-Length"])).decode() if "Content-Length" in headers else None

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
                    "body": body,  # TODO: handle base64 encoded case
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

                if enable_async:
                    queue.put({
                        "url": url,
                        "headers": headers,
                        "data": json.dumps(data),
                    })
                    self._send_response(200, {}, "")
                    return

                resp = requests.post(url, headers=headers, data=json.dumps(data))  # noqa

                if resp.status_code != 200:
                    # An error occured downstream, send status code and error message if any
                    self._send_response(resp.status_code, resp.headers, resp.content)
                    return

                # Parse response payload from lambda and return it
                try:
                    resp = json.loads(resp.content)
                except TypeError:
                    self._send_response(500, {}, f"Incorrect response type: \"{resp.content}\" is not valid JSON.")
                    return

                if not isinstance(resp, dict):
                    self._send_response(500, {}, f"Incorrect response type: \"{resp}\" is not a dictionary.")
                    return

                if "errorMessage" in resp:
                    self._send_response(500, {}, json.dumps(resp, indent=4))
                    return

                if resp.keys() < {"statusCode", "headers", "body"} or not isinstance(resp["headers"], dict):
                    self._send_response(500, {}, f"Malformed response payload: {json.dumps(resp)}. Keys 'statusCode', "
                                        "'headers', and 'body' are required.")
                    return

                self._send_response(resp["statusCode"], resp["headers"], resp["body"])

        server_address = ('', external_port)
        self.httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)

        # Start a separate thread to process async requests
        if enable_async:
            threading.Thread(target=process_requests).start()

        self.httpd.serve_forever()


def exit_now(signum, frame):
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="lambda-proxy",
        description="Proxy server to convert standard HTTP requests to Lambda POST requests via an API Gateway-like interface.",
    )
    parser.add_argument("hostname", help="Host name where the Lambda is running.")
    parser.add_argument("external_port", help="The port to expose the proxy on.", type=int)
    parser.add_argument("-i", "--internal-port", help="The port that the Lambda is running on.", default=8080, type=int)
    parser.add_argument("-a", "--enable-async", help="Run requests asynchronously. Causes proxy to return immediately with a "
                        "200 status code.", action="store_true")
    args = parser.parse_args()

    proxy = ApiProxy()
    signal.signal(signal.SIGTERM, exit_now)
    proxy.start_server(args.hostname, args.internal_port, args.external_port, args.enable_async)
