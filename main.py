'''Web Server Gateway Interface'''

from app import app

if __name__ == "__main__":    
    # app.run(ssl_context='adhoc')
    app.run(load_dotenv=True)
