import web

class MyWebApp(web.application):
    def __init__(self,urls_,globals_):
        web.application.__init__(self,urls_,globals_)

    def run(self,*args):
        print "running"
        web.application.run(self,*args)
        print "done!"

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
    def POST(self, name):
        if not name: 
            name = 'World'
        print "convert posted!"
        return 'Converted ' + name + ' to IDX, yay!'
        raise web.seeother("/convert/"+name+"_Converted")

    def GET(self, name):
        if not name: 
            name = 'World'
        return 'Converted ' + name + ' to IDX...'

class convert_it:
    def GET(self, name):
        if not name: 
            name = 'World=foo%20bar&hz=12'
        
        query=urlparse.parse_qs(name)
        print query
        return 'Converted ' + name + ' to IDX, bitches...'


if __name__ == "__main__":
    import urlparse
    urls = (
        '/GetIDX/(.*)', 'idxgen',
        '/convert/(.*)', 'convert',
        '/convert_it/(.*)', 'convert_it',
        '/(.*)', 'hello'
    )
    app = MyWebApp(urls, globals())
    app.run()

    print "app finished!"

