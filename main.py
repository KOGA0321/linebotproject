# main.py

import os
from app import create_app
import logging

app = create_app()

logging.basicConfig(level=logging.DEBUG)



if __name__ == "__main__":
    # PORT は環境変数から取るかデフォルト5000
    port = int(os.getenv("PORT", 5000))
    # 0.0.0.0 でバインドすると外部からもアクセス可
    app.run(host="0.0.0.0", port=port)


