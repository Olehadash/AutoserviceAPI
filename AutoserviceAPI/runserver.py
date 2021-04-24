"""
This script runs the AutoserviceAPI application using a development server.
"""

import os
from AutoserviceAPI import app, build_sample_db, socketio 

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    if not os.path.exists(database_path):
        build_sample_db()

    # Start app
    socketio.run(app, host = '0.0.0.0', port = 8080)
