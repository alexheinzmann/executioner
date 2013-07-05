from twisted.web.static import File
from twisted.web.server import Site
from twisted.internet import reactor
from executioner.api import ExecutionerApiHandler

root = File("executioner/www")  # Server folder www as static files
root.putChild("api", ExecutionerApiHandler())  # Let Api handler process /api

SERVER_PORT = 9000

factory = Site(root)
reactor.listenTCP(SERVER_PORT, factory)
reactor.run()
