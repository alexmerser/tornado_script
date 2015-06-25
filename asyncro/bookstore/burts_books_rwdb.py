#!/Users/kawasakitaku/Documents/python-PVM/ln-python3.4/bin/python3.4

import os.path

import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient

from tornado.options import define, options

import pymongo
import urllib
import json
import time
import datetime




define("port", default=8000, help="run on the given port", type=int)


class Application(tornado.web.Application):
	def __init__(self):
		handlers = [
			(r"/", MainHandler),
			(r"/recommended/", RecommendedHandler),
			(r"/edit/([0-9Xx\-]+)", BookEditHandler),
			(r"/add", BookEditHandler),
    ]
		settings = dict(
			template_path=os.path.join(os.path.dirname('.'), "templates"),
			static_path=os.path.join(os.path.dirname('.'), "static"),
			ui_modules={"Book": BookModule},
      debug=True,
			)
		conn = pymongo.Connection("localhost", 27017)
		self.db = conn["bookstore"]
		tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
  @tornado.web.asynchronous
  def get(self):
    client = tornado.httpclient.AsyncHTTPClient()
    client.fetch('index.html')
    self.render(
      "index.html",
      page_title = "PDF Books | Home",
      header_text = "Welcome to PDF Books!",
      )

class BookEditHandler(tornado.web.RequestHandler):
  @tornado.web.asynchronous
  def get(self, isbn=None):
    client = tornado.httpclient.AsyncHTTPClient()
    client.fetch('book_edit.html')
    book = dict()
    if isbn:
      coll = self.application.db.books
      book = coll.find_one({"isbn": isbn})
    self.render("book_edit.html",
              page_title="PDF Books",
              header_text="Edit book",
              book=book)

  @tornado.web.asynchronous
  def post(self, isbn=None):
    client = tornado.httpclient.AsyncHTTPClient()
    import time
    book_fields = ['isbn', 'title', 'subtitle', 'image', 'author',
                    'date_released', 'description']
    coll = self.application.db.books
    book = dict()
    if isbn:
      book = coll.find_one({"isbn": isbn})
    for key in book_fields:
      book[key] = self.get_argument(key, None)

    if isbn:
      coll.save(book)
    else:
      book['date_added'] = int(time.time())
      coll.insert(book)
    self.redirect("/recommended/")


    
class RecommendedHandler(tornado.web.RequestHandler):
  @tornado.web.asynchronous
  def get(self):
    client = tornado.httpclient.AsyncHTTPClient()
    client.fetch('recommended.html')
    coll = self.application.db.books
    books = coll.find()
    self.render(
      "recommended.html",
      page_title = "PDF Books | Recommended Reading",
      header_text = "Recommended Reading",
      books = books
    )
		
class BookModule(tornado.web.UIModule):
	def render(self, book):
		return self.render_string(
			"modules/book.html", 
			book=book,
		)
	
	def css_files(self):
		return "css/recommended.css"
	
	def javascript_files(self):
		return "js/recommended.js"


def main():
	tornado.options.parse_command_line()
	http_server = tornado.httpserver.HTTPServer(Application())
	http_server.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
  main()
