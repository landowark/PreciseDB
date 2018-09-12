import Flask.routes
import os



port = int(os.environ.get('PORT', 5000))
Flask.routes.app.run('localhost', port=port, debug=True)
