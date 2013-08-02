import json
import os
import sqlite3

from twisted.internet.threads import deferToThread
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET

from ansible import utils
from ansible.inventory import Inventory
import ansible.runner


def jsonify(request, ret):
    """
    Helper function to return json api response
    """
    request.setHeader('Content-Type', 'application/json')
    return json.dumps(ret)


def error_page(request):
    request.setResponseCode(500)
    return "Internal server error"
    
def validId(value):
    """
    Helper function to determine if the ID is valid
    """
    try:
        int(value)
    except ValueError:
        return False
    return True

class ExecutionerApiHandler(Resource):
    """
    Class to process all requests coming to the api.

    """
    isLeaf = False

    def __init__(self):
        Resource.__init__(self)
        #  Add resource types
        self.putChild('runcommand', RunCommandHandler())
        self.putChild('modules', ModuleHandler())
        self.putChild("inventory", InventoryHandler())
        self.putChild("commands", CommandManager())
        self.putChild("commandList", CommandHandler())
        self.putChild("", self)

    def render_GET(self, request):
        """
        Render list all resource types as json
        """
        ret = {"resourcetypes": [ \
            {"inventory":"/api/inventory"}, \
            {"modules":"/api/modules"},  \
            {"modules":"/api/runcommand"},  \
            {"commands":"/api/commands"},  \
            {"commandList":"/api/commandList"}  \
          ]}
        return jsonify(request, ret)
        
        
class CommandManager(Resource):
    """
    Manages the commands.  The user can read, create, update, and delete commands
    """
    isLeaf = True
    
    conn = sqlite3.connect('commands.db')
    with conn:
        cur = conn.cursor()
                    
        """
        if the table does not exist, create it       
        """
        cur.execute("CREATE TABLE IF NOT EXISTS Commands(Id INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Description TEXT, Module TEXT, Command TEXT)")         
          

    def render_GET(self, request):
        """
        Look up the requested command by id and return it, rendered as json.
        If the given ID is not valid, return None
        """
        id = self._get_argument(request, "id")
        conn = sqlite3.connect('commands.db')
        with conn:
            cur = conn.cursor()
            
            if (not validId(id)):
                return None
            
            cur.execute("SELECT * FROM Commands WHERE Id = " + id)
            
            command = cur.fetchone()
            
            return jsonify(request, command) 
        
    def render_PUT(self, request):
        """
        Update a command in the database.  The target command is found by ID.  First, remove the old command, then add the updated command.
        If the command at this ID does not exist, add it.
        If the given ID is not valid, return None.
        Returns the updated command, rendered as JSON
        """
        
        id = self._get_argument(request, "id")
        name = self._get_argument(request, "name")
        description = self._get_argument(request, "description")
        module = self._get_argument(request, "module")
        command = self._get_argument(request, "command")
 
        if (not validId(id)):
            return None
        
        entry = id + ",'" + name + "','" + description + "','" + module + "','" + command + "'"
        
        conn = sqlite3.connect('commands.db')
        with conn:
            cur = conn.cursor()
            
            """
            Fist, remove the old command, then add the new command       
            """ 
            cur.execute("DELETE FROM Commands WHERE Id = " + id)

            cur.execute("INSERT INTO Commands VALUES(" + entry + ")")
            
            """
            return the added command
            """
            cur.execute("SELECT * FROM Commands WHERE Id = " + id)
            command = cur.fetchone()
            
            return jsonify(request, command) 
        
        
    def render_POST(self, request):
        """
        Add a new command to the database.  The ID for the command is automatically generated.
        Returns the added command, rendered as json
        """
        
        name = self._get_argument(request, "name")
        description = self._get_argument(request, "description")
        module = self._get_argument(request, "module")
        command = self._get_argument(request, "command")
        
        entry =  "'" + name + "','" + description + "','" + module + "','" + command + "'"
        
        conn = sqlite3.connect('commands.db')
        with conn:
            cur = conn.cursor()
            
            cur.execute("INSERT INTO Commands (Name, Description, Module, Command) VALUES(" + entry + ")")
            
            """
            return the added command
            """
            """cur.execute("SELECT * FROM Commands WHERE Id = " + id)"""
            command = cur.fetchone()
            
            return jsonify(request, command) 
        
    def render_DELETE(self, request):
        """
        Delete the specified command from the database
        If the given ID is not valid, return None
        """
        id = self._get_argument(request, "id")
        
        if (not validId(id)):
                return None
        
        conn = sqlite3.connect('commands.db')
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM Commands WHERE Id = " + id)
            

    def _get_argument(self, request, name, default=""):
        try:
            arg = request.args[name]
            if len(arg) == 0:
                return default
            arg = arg[0]
        except:
            return default
        return arg


class InventoryHandler(Resource):
    """
      Renders in json list of hosts and groups from configured ansible
      inventory file.
    """

    isLeaf = True

    def render_GET(self, request):
        i = Inventory()
        inv = []
        try:
            hosts = i.get_hosts()
            groups = i.get_groups()
        except:
            return self.error_page(request)
        inv.extend([{"name": x.name, "type":"host"} for x in sorted(hosts)])
        inv.extend([{"name": x.name, "type":"group"} for x in sorted(groups)])
        return jsonify(request, inv)


class ModuleHandler(Resource):
    """
      Renders in json all the ansible modules.
    """

    isLeaf = True

    def render_GET(self, request):
        module_paths = utils.plugins.module_finder._get_paths()
        modules = set()
        for path in module_paths:
            if os.path.isdir(path):
                fs = os.listdir(path)
                modules = modules.union(fs)
        ret = [{"name":x} for x in sorted(modules)]
        return jsonify(request, ret)
        
class CommandHandler(Resource):
    """
    Renders in json all of the commands currently in the database
    """
    isLeaf = True
    
    def render_GET(self, request):
        conn = sqlite3.connect('commands.db')
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Commands")
            command = cur.fetchall()
            
            return jsonify(request, command)


class RunCommandHandler(Resource):
    """
     Runs ansible commands and renders the output as json.
     Long lasting jobs may cause timeout (TODO: test if it happens).
    """
    isLeaf = True

    def render_GET(self, request):
        host = self._get_argument(request, "host")
        module = self._get_argument(request, "module")
        attr = self._get_argument(request, "attr")
        d = deferToThread(self.runAnsibleCmd, request, host=host, module=module, attr=attr)
        d.addCallback(self._callback, request=request)
        d.addErrback(self._errback, request=request)
        return NOT_DONE_YET

    def runAnsibleCmd(self, request, host="", module="", attr=""):
        runner = ansible.runner.Runner(
           module_name=module,
           module_args=attr,
           pattern=host,
           forks=10
        )
        data = runner.run()
        return data

    def _callback(self, data, request=None):
        request.write(jsonify(request, {"runresult": data}))
        request.finish()
        return

    def _errback(self, data, request=None):
        request.write(jsonify(error_page(request)))
        request.finish()
        return

    def _get_argument(self, request, name, default=""):
        try:
            arg = request.args[name]
            if len(arg) == 0:
                return default
            arg = arg[0]
        except:
            return default
        return arg

