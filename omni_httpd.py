#!/usr/bin/env python
"""
simple HTTP server in python
serve a simple form to use the OMNI Downloader
"""
from validators import url as validate_url
from celery import chain
from omni_tasks import load, ytie

from bottle import template, get, post, request, run, error, abort, static_file, auth_basic, route, FormsDict, MultiDict
from hashlib import sha512 as create_hash

def check(user, pw):
    '''
    really basic user and password check
    use a SHA512 hashed password from .htpasswd-file and check if the entered username and password matches
    '''
    pw = create_hash(pw).hexdigest()
    with open('.htpasswd', 'r') as passdb:
        for line in passdb:
            pwd_user, pwd_pw = line.split(':')
            if pwd_user == user and pwd_pw.rstrip() == pw:
                return True
            return False

# serve the form
@get('/')
@auth_basic(check)
def serve_form():
    return static_file('form.html', root='.')

# handle the POST data from the form
@post('/')
@auth_basic(check)
def collect_form():
    values = {}
    for item in request.forms:
        value = request.forms.get(item)
        if not value:
            value = None
        values[item] = value

    # if we entered a url, is not valid, http400
    if 'url' in values.keys():
        if values['url'] and not validate_url(values['url']):
            abort(400, 'inval - ' + values['url'])
        # if we entered nothing - no url & no ids, http400
        if not values['url'] and not values['vid'] and not values['pid']:
            abort(400, 'empty')
    # if remove folder value if unset
    if 'folder' in values.keys() and not values['folder']:
        del values['folder']
    # answer to user, show values if debug = true
    if 'debug' in values.keys() and values['debug']:
        return template("{{dict}}", dict=values)
    return 'ok'

# serve files in ./src/
@route('/src/<filename>')
@auth_basic(check)
def server_static(filename):
    return static_file(filename, root='./src/')

run(host="0.0.0.0", port=4000)

###########################
#
#class Server(BaseHTTPRequestHandler):
#    """ define the http-handlers """
##    def _set_headers(self, is_url):
##        """ build and send http response """
##        # if url is valid, 200 OK
##        if is_url:
##            self.send_response(200)
##        # else 400 Bad Request
##        else:
##            self.send_response(400)
##        self.send_header('Content-type', 'text/html')
##        self.end_headers()
#
##    def do_POST(self):
##        length = int(self.headers.getheader('content-length'))
##        field_data = self.rfile.read(length)
##        fields = urlparse.parse_qs(field_data)
##        print length
##        print field_data
##        print fields
#
#    def do_GET(self):
#        """ define the GET handler """
#        print(parse_qs(urlparse(self.path).query))
#        print(urlparse(self.path))
#        #field_data = self.rfile.read(length)
#        #fields = urlparse.parse_qs(field_data)
#        #print field_data
#        #print fields
#        # get the url-path
#        seife = self.path
#        # extract url and options from it
#        values = seife[1:].split('::')
#        # validate if url is a valid url
#        is_url = validators.url(values[0])
#
#        app = Bottle()
#
#        app.route()
##        self._set_headers(is_url)
##        self.wfile.write("<html><body>")
##        if is_url:
##            self.wfile.write("<p>200</p>")
##        else:
##            self.wfile.write("<p>400</p>")
##        self.wfile.write("<p>%s</p></body></html>" % seife)
#
#        #if is_url:
#        #    # start the celery chain
#        #    chain(load.s([seife]), ytie.s()).apply_async()
#
#@route('/note') # or @route('/note')
#def note():
#    return '''
#        <form action="/note" method="post">
#            <textarea cols="40" rows="5" name="note">
#            Some initial text, if needed
#            </textarea>
#            <input value="submit" type="submit" />
#        </form>
#    '''
#
#@post('/note') # or @route('/note', method='POST')
#def note_update():
#    note = bottle.request.forms.get('note')
#    # processing the content of the text frame hereV
#
#def run(server_class=HTTPServer, handler_class=Server, port=8000):
#    """ setting up the server parameter """
#    server_address = ('', port)
#    httpd = server_class(server_address, handler_class)
#    print 'Starting httpd on port ' + str(port)
#    httpd.serve_forever()
#
#if __name__ == "__main__":
#    run()
