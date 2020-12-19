from modules import application,db
from flask import send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint


@application.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static',path)

SWAGGER_URL='/swagger'
API_URL='/static/swagger.json'
swaggerui_blueprint=get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name':'Flask game forum rest API'
    }
)
application.register_blueprint(swaggerui_blueprint,url_prefix=SWAGGER_URL)




if __name__=='__main__':
    application.run(debug=True)
