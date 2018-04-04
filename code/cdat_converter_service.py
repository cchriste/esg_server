#***************************************************
#** ViSUS Visualization Project                    **
#** Copyright (c) 2010 University of Utah          **
#** Scientific Computing and Imaging Institute     **
#** 72 S Central Campus Drive, Room 3750           **
#** Salt Lake City, UT 84112                       **
#**                                                **
#** For information about this project see:        **
#** http:#www.pascucci.org/visus/                 **
#**                                                **
#**      or contact: pascucci@sci.utah.edu         **
#**                                                **
#****************************************************
#
#
# cdat_converter.py
#
# 1) Listens for http requests to convert a box of a resolution of a timestep of a field of a dataset.
# 2) Ensures there are not already conversions in progress.
# 3) Converts data.
# 4) Signals caller upon completion.
#
#****************************************************

import time
import sqlite3
import visuspy as Visus
import VisusIdxPy
import VisusKernelPy
import SocketServer
import BaseHTTPServer
import fcntl
import cdms2
import urlparse
import os
import socket
from sys import stdout
from shutil import rmtree
import cdat_to_idx
import convert_query


RESULT_SUCCESS=200; RESULT_INVALID=400; RESULT_NOTFOUND=404; RESULT_ERROR=500; RESULT_BUSY=503

class cdatConverter(BaseHTTPServer.BaseHTTPRequestHandler):
    """http request handler for cdat to idx conversion requests"""

    nqueries_=0

    def do_GET(self):
        url=urlparse.urlparse(self.path)
        if url.path=='/convert':
            query_id=cdatConverter.nqueries_; cdatConverter.nqueries_+=1
            t1=time.time()
            print "("+str(query_id)+") started: ",url.query
            stdout.flush()
            try:
                result,response=call_convert_query(url.query)
            except Exception as e:
                print "Exception: ",e
                raise
            print "("+str(query_id)+") complete ("+str((time.time()-t1)*1000)+"ms): ["+str(response)+"] "+result,url.query
            stdout.flush()
            self.send_response(response)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write("<html><head></head><body>"+result+"</body></html>")
            return
        if url.path=='/create':
            print "request received: "+url.query
            result,response=create(url.query)
            self.send_response(response)
            if response != RESULT_SUCCESS:
                self.send_header('Content-type','text/html')
            else:
                self.send_header('Content-type','application/xml; charset=utf-8')
            self.end_headers()
            if response != RESULT_SUCCESS:
                self.wfile.write("<html><head></head><body>"+result+"</body></html>")
            else:
                self.wfile.write(result)
            stdout.flush()
            return
        if url.path=='/clear':
            result,response=clear_cache()
            self.send_response(response)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write("<html><head></head><body>"+result+"</body></html>")
            stdout.flush()
            return


def clear_cache():
    """clear a specific cache directory. Be careful with this!!!"""
    result="sample cache cleared."
    try:
        rmtree("/for_ganzberger1/idx/idx/acme-test.ORNL.HIGHRES.init.all.v1-lon_lat_ilev_time")
        rmtree("/for_ganzberger1/idx/idx/acme-test.ORNL.HIGHRES.init.all.v1-lon_lat_lev_time")
        rmtree("/for_ganzberger1/idx/idx/acme-test.ORNL.HIGHRES.init.all.v1-lon_lat_time")
    except OSError as e:
        result="OSError: "+str(e)
    return result,RESULT_SUCCESS



def parse_query(query):
    """parse the cdat to idx conversion query string"""

    job=urlparse.parse_qs(query)
    idxpath=None
    field=None
    timestep=0
    box=None
    hz=-1
    if job.has_key("idx"):
        idxpath=job["idx"][0]
    if job.has_key("time"):
        timestep=int(float(job["time"][0]))
    if job.has_key("field"):
        field=job["field"][0]
        idx=field.find('?')
        if idx>=0:                  # field time overrides query time
            field=field[:idx]
            arg=field[idx+1:]
            if arg.startswith("time="):
                timestep=int(arg[arg.find('=')+1:])
    if job.has_key("box"):
        box=job["box"][0]
    if job.has_key("hz"):
        hz=int(job["hz"][0])
    return idxpath,field,timestep,box,hz


def parse_return(args_str):
    print "parse_return:",args_str
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--code"    ,default=200,type=int,help="return code")
    parser.add_argument("-s","--string",default="This is a test",help="return string")
    args_str=args_str[args_str.find("-c"):] #filter visus copyright message
    #print "args str:",args_str
    args = parser.parse_args(args_str.split(";"))
    #print "args:",args
    #print "returning ("+args.string+","+str(args.code)+")"
    return (args.string,args.code)

def call_convert_query(query):
    """Converts a timestep of a field of a cdat dataset to idx, using the idxpath to find the matching cdat volume."""

    # parse query request
    try:
        idxpath,field,timestep,box,hz=parse_query(query)
        print idxpath,field,timestep,box,hz

    except Exception as e:
        print "Exception: ",e
        raise
 
    if not idxpath or not field:
        return ("Invalid query: %s"%query,RESULT_INVALID)
    
    try:
        global dbpath
        ret=convert_query.convert(idxpath,field,timestep,box,hz,dbpath)
        print "ret:",ret
        return ret #parse_return(ret)
    except Exception as e:
        print "Exception:",e
        raise
    # from subprocess import check_output,CalledProcessError
    # try:
    #     global dbpath
    #     cmd=["python","-c","import convert_query; convert_query.convert(\""+idxpath+"\",\""+field+"\","+str(timestep)+",\""+box+"\","+str(hz)+",\""+dbpath+"\")"]
    #     #print "cmd:",cmd
    #     ret=check_output(cmd,shell=False)
    #     #print "ret:",ret
    #     return parse_return(ret)
    # #except CalledProcessError as e:
    # except Exception as e:
    #     #TODO: probably some error handling here
    #     print "Exception:",e
    #     raise


def create(query):
    """Create idx volumes corresponding to cdat dataset (xml or nc)."""

    t1 = time.clock()

    result_str="An unknown error occurred."
    result=RESULT_ERROR
    try:
        # parse query request
        job=urlparse.parse_qs(query, True, True)   #keep empty fields, strict checking
        if not job.has_key("dataset"):
            raise ConvertError(RESULT_INVALID,"Query must specify a valid and accessible .xml or .nc file and destination path")

        global xml_path,idx_path,ondemand_service_address,dbpath,visusserver,visusserver_username,visusserver_password
        cdatpath=xml_path+"/"+job["dataset"][0]
        idxpath=idx_path
        if job.has_key("destination"):
            idxpath=idx_path+"/"+job["destination"][0]
        server=visusserver
        if job.has_key("server"):
            server=job["server"][0]
        username=visusserver_username
        if job.has_key("username"):
            username=job["username"][0]
        password=visusserver_password
        if job.has_key("password"):
            password=job["password"][0]
        force=False
        if job.has_key("force"):
            if job["force"][0]=="True" or job["force"][0]=="1" or job["force"][0]=="true":
                print "forcing job!!! (force="+job["force"][0]+")"
                force=True

        # create idx volumes from climate dataset
        import cdat_to_idx
        print "generate_idx(inputfile=",cdatpath,",outputdir=",idxpath,",database=",dbpath,",server=",server,",username=",username,",password=",password,",service=",ondemand_service_address,",force=",str(force),")"
        result_str=cdat_to_idx.generate_idx(inputfile=cdatpath,outputdir=idxpath,database=dbpath,server=server,username=username,password=password,service=ondemand_service_address,force=force)
        result=RESULT_SUCCESS

    except ConvertError as e:
        result=e.code
        result_str=e.msg
    except Exception as e:
        result=RESULT_ERROR
        result_str="unknown error occurred during create ("+str(e)+")"

    print "result_str: "+result_str
    print "result: "+str(result)
    return (result_str,result)


def init(database,hostname,port,xmlpath,idxpath,visus_server,username,password):
    VisusKernelPy.SetCommandLine("__main__")
    VisusIdxPy.IdxModule.attach()

    global dbpath
    dbpath=database
    if not dbpath:
        dbpath=idxpath+"/idx.db"

    global ondemand_service_address
    ondemand_service_address="http://"+hostname+":"+str(port)

    global xml_path
    xml_path=xmlpath

    global idx_path
    idx_path=idxpath

    global visusserver
    visusserver=visus_server

    global visusserver_username
    visusserver_username=username

    global visusserver_password
    visusserver_password=password

#note: doesn't seem to be any huge reason in our case to prefer forking over theading, but both work fine
class OnDemandSocketServer(SocketServer.ThreadingTCPServer):
#class OnDemandSocketServer(SocketServer.ForkingTCPServer):
    """This is just to override handle_error to be less annoying when disconnections occur
    """
    def handle_error(self, request, client_address):
        """Handle an error gracefully.  May be overridden.
        The default is to print a traceback and continue.
        """
        if False:
            print '-'*40
            print 'Exception happened during processing of request from',
            print client_address
            import traceback
            traceback.print_exc() # XXX But this goes to stderr!
            print '-'*40


def start_server(hostname,port):
    # start server
    SocketServer.ThreadingTCPServer.allow_reuse_address = True
    #SocketServer.ForkingTCPServer.allow_reuse_address = True
    httpd = OnDemandSocketServer((hostname, port),cdatConverter)
    httpd.request_queue_size=socket.SOMAXCONN
    print "serving at port", port
    stdout.flush()
    try:
        httpd.serve_forever()
    except:
        pass

    httpd.shutdown()

# ############################
if __name__ == '__main__':

    # converter service default
    default_idx_db_path="/for_ganzberger1/idx/idx/idx.db"
    default_port=42299
    default_host="localhost"

    # cdat_to_idx defaults
    default_server="http://localhost:10000/mod_visus"
    default_xml_path="/data/xml/"
    default_idx_path="/data/idx/"

    import argparse
    parser = argparse.ArgumentParser(description="Convert CDAT data to IDX format.")
    parser.add_argument("-p","--port"    ,default=default_port,type=int,help="listen on port")
    parser.add_argument("-l","--hostname",default=default_host,help="ip address or hostname on which to listen")
    parser.add_argument("-x","--xmlpath",default=default_xml_path,help="path to cdat xml files created with uv-cdat cdscan utility")
    parser.add_argument("-i","--idxpath",default=default_idx_path,help="path to place newly created idx volumes")
    parser.add_argument("-d","--database",help="path to cdat-to-database (default is $IDX_PATH/idx.db)")
    parser.add_argument("-s","--visusserver",default=default_server,help="visus server with which to register newly created idx volumes")
    parser.add_argument("--username",default="root",help="username to register newly created idx volumes with server")
    parser.add_argument("--password",default="visus",help="password to register newly created idx volumes with server")
    args = parser.parse_args()

    init(args.database,args.hostname,args.port,args.xmlpath,args.idxpath,args.visusserver,args.username,args.password)

    print "Starting server http://"+args.hostname+":"+str(args.port)+"..."
    print "\txml path: "+xml_path
    print "\tidx path: "+idx_path
    print "\tdatabase: "+dbpath
    print "\tvisus server: "+visusserver
    print "\tmax sockets:",socket.SOMAXCONN
    start_server(args.hostname,args.port)
    VisusIdxPy.IdxModule.detach()

    print "done!"
