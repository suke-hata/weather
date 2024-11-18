import os
from flask import Flask

def create_app():
    app = Flask(__name__)
    
    app.secret_key = 'your_secret_key'
    
    # Blueprintをインポートし、登録する
    from flaskr.main import main
    app.register_blueprint(main)

    # 他の設定やBlueprintの登録を行う

    return app

import flaskr.main
