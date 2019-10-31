# Setup an Instant S3-backed NoSQL HTTP Database

import sys,subprocess,os,datetime
import requests as http

THIS_DIR = os.getcwd()
if "\\" in THIS_DIR:
    slash = "\\"; sudo = ""
else:
    slash = "/"; sudo = "sudo "
THIS_DIR+=slash

config_file = THIS_DIR+"S3AppDatabase.config"
gateway_file_url = "https://raw.githubusercontent.com/cmdimkpa/S3AppDatabaseWorker/master/DBGateway.js"
servlet_file_url = "https://raw.githubusercontent.com/cmdimkpa/S3AppDatabaseWorker/master/S3AppDatabaseWorker.py"

BUILD_SECONDS = 0

def now():
    return datetime.datetime.today()

def elapsed(t):
    return (now() - t).seconds

def report(task,breakpoint):
    global BUILD_SECONDS
    lasted = elapsed(breakpoint)
    BUILD_SECONDS+=lasted
    print("Completed task: %s, took: %s secs" % (task,lasted))

def read_config():
    p = open(config_file,"rb+")
    config = p.readlines()
    p.close()
    return {line.split("\r\n")[0].split(":")[0]:line.split("\r\n")[0].split(":")[1] for line in config}

def write_config(config):
    p = open(config_file,"wb+")
    lines = ["%s:%s\r\n" % (key,config[key]) for key in config]
    p.writelines(lines)
    p.close()
    return config

def make_gateway_file(src):
    gateway_file = THIS_DIR+"DBGateway.js"; p = open(gateway_file,"wb+"); p.write(src); p.close()
    package_file = THIS_DIR+"package.json"; p = open(package_file,"wb+"); p.write("{}"); p.close()
    return gateway_file

def make_servlet_file(src):
    servlet_file = THIS_DIR+"DBServlet.py"; p = open(servlet_file,"wb+"); p.write(src); p.close()
    return servlet_file

def run_shell(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = p.communicate()
    if err:
        return err
    else:
        try:
            return eval(out)
        except:
            return out

class ConfigEvent:
    def __init__(self,eventType):
        self.eventType = eventType
    def run(self):
        if self.eventType == "rebuild_config":
            RunEvent("stop_config")
            RunEvent("build_config")
        else:
            RunEvent(self.eventType)

def RunEvent(mode):
    if mode == "edit_config":
        default_config = {
            "s3bucket_name":None,
            "s3conn_user":None,
            "s3conn_pass":None,
            "s3region":None,
            "server_host":None,
            "server_port":None
        }
        try:
            config = read_config()
            if not config:
                config = default_config
        except:
            config = default_config
        for key in config:
            print("%s: ? %s" % (key,config[key]))
            entry = raw_input()
            if entry:
                config[key] = entry
        print(write_config(config))
    elif mode == "show_config":
        try:
            print(read_config())
        except:
            print(write_config({}))
    elif mode == "import_config":
        try:
            url = sys.argv[2]
            try:
                config = eval(http.get(url).content)
                print(write_config(config))
            except:
                print("Config file Not JSON Serializable, exiting...")
                sys.exit()
        except:
            print("Import URL not found, Exiting...")
            sys.exit()
    elif mode == "stop_config":
        try:
            run_shell("cd %s" % THIS_DIR)
            print(run_shell("%sforever stop -c node DBGateway.js" % sudo))
            print(run_shell("%sforever stop -c pypy DBServlet.py" % sudo))
        except Exception as e:
            print("Error: %s" % str(e))
            sys.exit()
    elif mode == "build_config":
        try:
            BUILD_STAGES = 2
            BUILD_STAGE = 1
            BUILD_STAGE_DESCR = "Create Gateway Node Environment"
            BUILD_TASK = "Download gateway file"; breakpoint = now()
            gateway_src = http.get(gateway_file_url).content
            report(BUILD_TASK,breakpoint)
            BUILD_TASK = "Read Config"; breakpoint = now()
            Config = read_config()
            report(BUILD_TASK,breakpoint)
            BUILD_TASK = "Update environment variables"; breakpoint = now()
            gateway_src = gateway_src.replace("__DB_GATEWAY_PORT__",Config["server_port"])
            gateway_src = gateway_src.replace("__DB_SERVER_HOST__",Config["server_host"])
            gateway_src = gateway_src.replace("__DB_SERVER_PORT__",str(int(Config["server_port"])+1))
            gateway_file = make_gateway_file(gateway_src)
            print("gateway file: %s" % gateway_file)
            report(BUILD_TASK,breakpoint)
            BUILD_TASK = "Set Install Path"; breakpoint = now()
            run_shell("cd %s" % THIS_DIR)
            report(BUILD_TASK,breakpoint)
            BUILD_TASK = "Require Node Modules"; breakpoint = now()
            print(run_shell("%snpm install --save express body-parser request cors compression" % sudo))
            print(run_shell("%snpm install -g forever" % sudo))
            report(BUILD_TASK,breakpoint)
            BUILD_TASK = "Start Gateway Service"; breakpoint = now()
            print(run_shell("%sforever start -c node DBGateway.js" % sudo))
            report(BUILD_TASK,breakpoint)
            BUILD_STAGE = 2
            BUILD_STAGE_DESCR = "Create PyPy Database Servlet Environment"
            BUILD_TASK = "Download DB Servlet file"; breakpoint = now()
            db_servlet_file = make_servlet_file(http.get(servlet_file_url).content)
            print("Servlet file: %s" % db_servlet_file)
            report(BUILD_TASK,breakpoint)
            BUILD_TASK = "Require PyPy modules"; breakpoint = now()
            # require pip
            p = open(THIS_DIR+"get-pip.py","wb+"); p.write(http.get("https://bootstrap.pypa.io/get-pip.py").content); p.close()
            print(run_shell("%spypy get-pip.py" % sudo))
            # require modules
            print(run_shell("%spypy -m pip install flask flask_cors boto eventlet flask-socketio" % sudo))
            report(BUILD_TASK,breakpoint)
            BUILD_TASK = "Run pypy Servlet"; breakpoint = now()
            print(run_shell("%sforever start -c pypy DBServlet.py %s %s %s %s %s %s" % (sudo,Config["s3bucket_name"],Config["s3conn_user"],Config["s3conn_pass"],Config["s3region"],Config["server_host"],int(Config["server_port"])+1)))
            report(BUILD_TASK,breakpoint)
            print("Database API Running on: http://%s:%s/ods/" % (Config["server_host"],Config["server_port"]))
            print("BUILD LASTED: %s seconds" % BUILD_SECONDS)
            sys.exit()
        except Exception as error:
            print("BuildError: [Build Stage: %s/%s, Build Process: %s -> %s] : %s" % (BUILD_STAGE,BUILD_STAGES,BUILD_STAGE_DESCR,BUILD_TASK,str(error)))
    else:
        print("mode: [%s] unknown, exiting..." % mode)
        sys.exit()

try:
    CONFIG_MODE = sys.argv[1]
    event = ConfigEvent(CONFIG_MODE)
    event.run()
except:
    print("No mode selected. Exiting...")
    sys.exit()
