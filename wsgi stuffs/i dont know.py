from wsgiref.simple_server import make_server
from urllib.parse import  parse_qs
from html import escape


html_content='''
<html>
<body>
   <form method="post" action="">
        <p>
           Age: <input type="text" name="age" value="%(age)s">
        </p>
        <p>
            Hobbies:
            <input
                name="hobbies" type="checkbox" value="software"
                %(checked-software)s
            > Software
            <input
                name="hobbies" type="checkbox" value="tunning"
                %(checked-tunning)s
            > Auto Tunning
        </p>
        <p>
            <input type="submit" value="Submit">
        </p>
    </form>
    <p>
        Age: %(age)s<br>
        Hobbies: %(hobbies)s
    </p>
</body>
</html>
'''




def application(environ,start_response):
    try:
        request_body_size=int(environ.get('CONTENT_LENGTH'),0)
    except(ValueError):
        request_body_size=0

    request_body=environ['wsgi.input'].read(request_body_size)
    d=parse_qs(request_body)

    age=d.get('age',[''])[0]
    hobbies=d.get('hobbies',[])
    age=escape(age)
    hobbies=[escape(hobbie) for hobbie in hobbies]

    response_body=html_content%{
        'checked-software':('','checked')['software' in hobbies],
        'checked-tunning':('','checked')['tunning' in hobbies],
        'age':age or'Empty',
        'hobbies':', '.join(hobbies)or ['No Hobbies?']
    }

    status='200 OK'

    response_headers=[
        ('Content-type','text/html'),
        ('Content-length',str(len(request_body)))
    ]

    start_response(status,response_headers)
    return [response_body.encode()]


httpd=make_server(
    'localhost',
    8000,
    application
)

