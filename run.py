from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Использование переменных окружения или значений по умолчанию
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)