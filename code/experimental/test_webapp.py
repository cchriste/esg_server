import web
        
urls = (
    '/GetIDX/(.*)', 'idxgen',
    '/convert/(.*)', 'convert',
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

class convert:        
    def GET(self, name):
        if not name: 
            name = 'World'
        return 'Converting ' + name + ' to IDX...'

if __name__ == "__main__":
    app.run()
