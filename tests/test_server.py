import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from app import Handler


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join()

    def request(self,method,path,body=None,headers=None):
        connection=HTTPConnection("127.0.0.1",self.server.server_port,timeout=5)
        h={"Host":f"127.0.0.1:{self.server.server_port}"}
        if headers:h.update(headers)
        connection.request(method,path,body,h)
        response=connection.getresponse()
        status,data,meta=response.status,response.read(),dict(response.getheaders())
        connection.close()
        return status,data,meta

    def test_home_and_all_assets(self):
        for path in ["/","/app.js","/style.css","/favicon.svg","/api/demo","/api/health"]:
            with self.subTest(path=path):
                status,data,headers=self.request("GET",path)
                self.assertEqual(status,200);self.assertTrue(data)
                self.assertIn("nosniff",headers["X-Content-Type-Options"])

    def test_demo_analyze_and_export(self):
        _,body,_=self.request("GET","/api/demo")
        payload=json.dumps({"csv":json.loads(body)["csv"]})
        for path in ["/api/analyze","/api/export/csv"]:
            with self.subTest(path=path):
                status,data,_=self.request("POST",path,payload,{"Content-Type":"application/json"})
                self.assertEqual(status,200)
                self.assertIn(b"Q-01",data)

    def test_errors_are_actionable(self):
        for body in ['{bad','[]',json.dumps({"csv":"bad"}),json.dumps({"rows":[1]})]:
            with self.subTest(body=body):
                status,data,_=self.request("POST","/api/analyze",body)
                self.assertEqual(status,400);self.assertIn("error",json.loads(data))

    def test_no_file_traversal_or_private_sources(self):
        for path in ["/../app.py","/app.py","/data/demo.csv","/submission/devpost.md"]:
            self.assertEqual(self.request("GET",path)[0],404)

    def test_host_and_cross_origin_rejected(self):
        self.assertEqual(self.request("GET","/",headers={"Host":"evil.example"})[0],403)
        self.assertEqual(self.request("POST","/api/analyze","{}",{"Origin":"https://evil.example"})[0],403)

    def test_empty_and_large_requests_rejected(self):
        self.assertEqual(self.request("POST","/api/analyze","")[0],413)
        self.assertEqual(self.request("POST","/api/analyze","{}",{"Content-Length":"2500001"})[0],413)


if __name__ == "__main__":
    unittest.main()
