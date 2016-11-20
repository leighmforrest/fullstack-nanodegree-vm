from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

# Set up the database code
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()



form = """
<form method='post' enctype='multipart/form-data' action='/new'>
    <h2>Add New Restaurant</h2>
    <input name='restaurant' type='text'><input type='submit' value='Submit'>
</form>
"""

update_form = "<form method='post' enctype='multipart/form-data' action='/%s/edit'>"
update_form += "<h2>Edit Restaurant</h2>"
update_form += '<input name="restaurant" type="text" value="%s">'
update_form += "<input type='submit' value='Submit'>"
update_form += "</form>"

delete_form = "<form method='post' enctype='multipart/form-data' action='/%s/delete'>"
delete_form += "<h2>Do you wish to delete this %s?</h2>"
delete_form += "<input type='submit' value='Delete'>"
delete_form += '</form>'



class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                # Get the data to be sent to browser
                restaurants = session.query(Restaurant.id, Restaurant.name).all()

                # Output all of the restaurants
                output = ""
                output += "<html><body><h1>Restaurants</h1><ul>"
                for restaurant in restaurants:
                    output += "<li>{0}<a href='/{1}/edit'>Update</a><a href='/{1}/delete'>Delete</a></li>".format(restaurant.name, restaurant.id)

                output += "<a href='/new'>Add New Restaurant</a>"
                output += "</ul></body></html>"
                # output += form
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body><h1>New Restaurant</h1>"
                output += form
                output += "<a href=\"/\">Back to Homepage</a></body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("edit"):
                restaurant_id = self.path.split("/")[1]
                restaurant = session.query(
                    Restaurant).filter_by(id=restaurant_id).one()
                if restaurant != []:

                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                output = ""
                output += "<html><body><h1>Edit Restaurant</h1>"
                output += update_form % (restaurant.id, restaurant.name)
                output += "<a href=\"/\">Back to Homepage</a></body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("delete"):
                restaurant_id = self.path.split("/")[1]
                restaurant = session.query(
                    Restaurant).filter_by(id=restaurant_id).one()
                if restaurant != []:

                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                output = ""
                output += "<html><body><h1>Delete Restaurant</h1>"
                output += delete_form % (restaurant.id, restaurant.name)
                output += "<a href=\"/\">Back to Homepage</a></body></html>"
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restaurant')
                # persist to database
                new_restaurant = Restaurant(name=messagecontent[0])
                session.add(new_restaurant)
                session.commit()

                # Redirect to
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/')
                self.end_headers()

            if self.path.endswith("edit"):
                restaurant_id = self.path.split("/")[1]
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restaurant')
                # persist to database
                old_restaurant = session.query(
                    Restaurant).filter_by(id=restaurant_id).one()
                if old_restaurant != []:
                    old_restaurant.name = messagecontent[0]
                    session.add(old_restaurant)
                    session.commit()

            if self.path.endswith("delete"):
                restaurant_id = self.path.split("/")[1]
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                # persist to database
                old_restaurant = session.query(
                    Restaurant).filter_by(id=restaurant_id).one()
                if old_restaurant != []:
                    session.delete(old_restaurant)
                    session.commit()

                # Redirect to
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/')
                self.end_headers()
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()


if __name__ == '__main__':
    main()
