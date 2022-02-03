from http.server import BaseHTTPRequestHandler, HTTPServer


class TasksCommand:
    TASKS_FILE = "tasks.txt"
    COMPLETED_TASKS_FILE = "completed.txt"

    current_items = {}
    completed_items = []

    def read_current(self):
        try:
            file = open(self.TASKS_FILE, "r")
            for line in file.readlines():
                item = line[:-1].split(" ")
                self.current_items[int(item[0])] = " ".join(item[1:])
            file.close()
        except Exception:
            pass

    def read_completed(self):
        try:
            file = open(self.COMPLETED_TASKS_FILE, "r")
            self.completed_items = file.readlines()
            file.close()
        except Exception:
            pass

    def write_current(self):
        with open(self.TASKS_FILE, "w+") as f:
            f.truncate(0)
            for key in sorted(self.current_items.keys()):
                f.write(f"{key} {self.current_items[key]}\n")

    def write_completed(self):
        with open(self.COMPLETED_TASKS_FILE, "w+") as f:
            f.truncate(0)
            for item in self.completed_items:
                f.write(f"{item}\n")

    def runserver(self):
        address = "127.0.0.1"
        port = 8000
        server_address = (address, port)
        httpd = HTTPServer(server_address, TasksServer)
        print(f"Started HTTP Server on http://{address}:{port}")
        httpd.serve_forever()

    def run(self, command, args):
        self.read_current()
        self.read_completed()
        if command == "add":
            self.add(args)
        elif command == "done":
            self.done(args)
        elif command == "delete":
            self.delete(args)
        elif command == "ls":
            self.ls()
        elif command == "report":
            self.report()
        elif command == "runserver":
            self.runserver()
        elif command == "help":
            self.help()

    def help(self):
        print(
            """Usage :-
$ python tasks.py add 2 hello world # Add a new item with priority 2 and text "hello world" to the list
$ python tasks.py ls # Show incomplete priority list items sorted by priority in ascending order
$ python tasks.py del PRIORITY_NUMBER # Delete the incomplete item with the given priority number
$ python tasks.py done PRIORITY_NUMBER # Mark the incomplete item with the given PRIORITY_NUMBER as complete
$ python tasks.py help # Show usage
$ python tasks.py report # Statistics
$ python tasks.py runserver # Starts the tasks management server"""
        )

    def add(self, args):
        try:
            self.read_current()
            if int(args[0]) in self.current_items.keys():
                call = []
                old_item = self.current_items[int(args[0])]
                new_priority = int(args[0]) + 1
                call.append(new_priority)
                call.append(old_item)
                self.add(call)
                self.current_items[int(args[0])] = args[1]
            else:
                self.current_items[int(args[0])] = args[1]
            self.write_current()
            print(f"Added task: \"{args[1]}\" with priority {args[0]}")
        except Exception:
            print("here")

    def done(self, args):
        try:
            self.read_current()
            self.read_completed()
            item = self.current_items[int(args[0])]
            self.completed_items.append(item)
            del self.current_items[int(args[0])]
            self.write_current()
            self.write_completed()
            print("Marked item as done.")
        except Exception:
            print(f"Error: no incomplete item with priority {args[0]} exists.")

    def delete(self, args):
        try:
            self.read_current()
            del self.current_items[int(args[0])]
            self.write_current()
            print(f"Deleted item with priority {args[0]}")
        except Exception:
            print(f"Error: item with priority {args[0]} does not exist. Nothing deleted.")

    def ls(self):
        self.read_current()
        i = 1
        for priority, task in self.current_items.items():
            print(f"{i}. {task} [{priority}]")
            i = i + 1

    def report(self):
        self.read_current()
        self.read_completed()
        print(f"Pending : {len(self.current_items)}")
        i = 1
        for priority, task in self.current_items.items():
            print(f"{i}. {task} [{priority}]")
            i = i + 1
        print(f"\nCompleted : {len(self.completed_items)}")
        i = 1
        for item in self.completed_items:
            print(f"{i}. {item}")
            i = i + 1

    def render_pending_tasks(self):
        self.read_current()
        list_items = []
        list_items.append("<tr> <th>Priotity</th> <th>Task</th> </tr>")
        for priority, task in self.current_items.items():
            list_items.append(f"<tr> <td> {priority} </td> <td> {task} </td> </tr>")
        content = "<table>" + "".join(list_items) + "</table>"
        return "<h1> Show Incomplete Tasks Here </h1>" + content

    def render_completed_tasks(self):
        self.read_completed()
        list_items = []
        for task in self.completed_items:
            list_items.append(f"<li> {task} </li>")
        content = "<ul>" + "".join(list_items) + "</ul>"
        return "<h1> Show Completed Tasks Here </h1>" + content


class TasksServer(TasksCommand, BaseHTTPRequestHandler):
    def do_GET(self):
        task_command_object = TasksCommand()
        if self.path == "/tasks":
            content = task_command_object.render_pending_tasks()
        elif self.path == "/completed":
            content = task_command_object.render_completed_tasks()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())
