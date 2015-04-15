import web
        
urls = (
    '/GetIDX/(.*)', 'idxgen',
    '/readdata/(.*)', 'convert',
    '/(.*)', 'hello'
)
app = web.application(urls, globals())

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

class readdata:        
    def GET(self, name):
        if not name: 
            name = 'World'
        return 'Converting ' + name + ' to IDX...'

if __name__ == "__main__":
    app.run()
