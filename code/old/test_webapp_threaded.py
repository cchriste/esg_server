import web
import threading

urls = (
    '/GetIDX/(.*)', 'idxgen',
    '/convert/(.*)', 'convert',
    '/(.*)', 'hello'
)

class MyThread(web.application,threading.Thread):
    def __init__(self,urls_,globals_):
        web.application.__init__(self,urls_,globals_)
        threading.Thread.__init__(self)

    def run(self,*args):
        print "running"
        web.application.run(self,*args)
        print "done!"


threads = []

# Create new threads
for i in range(10):
    thread = MyThread(urls,globals())
    thread.start()
    threads.append(thread)


# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"


class hello:        
    def GET(self, name):
        if not name: 
            name = 'World'
        return 'Hello, ' + name + '!'

class idxgen:
    def GET(self, name):
        if not name: 
            name = 'World'
        return 'Generating IDX for dataset ' + name + '...'

class convert:        
    def GET(self, name):
        if not name: 
            name = 'World'
        return 'Converting ' + name + ' to IDX...'

if __name__ == "__main__":
    app.run()
