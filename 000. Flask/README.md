# Flask
작고 강력한 파이썬의 서버 프레임워크
~~~
pip install flask
~~~

## 개요
Python으로 작성된 마이크로 서버 프레임워크. 두개의 외부 라이브러리(Jinja2 템플릿 엔진, Werkzeug WSGI 툴킷)에 의존하고 있음. Flask의 '마이크로'는 핵싱 기능만 간결하게 유지하되 쉽게 확장 가능한 것을 목적으로 한다는 의미를 가지고 있다.

Flask는 내부적으로 Thread local 방식을 사용한다. Thread-safe한 상태를 유지하기 위해서 하나의 요청에서 함수들이 돌아가며 객체를 주고받을 필요가 없도록 했다. 이 때문에 문맥(Context)를 이해하는 일이 매우 중요하다.

## Flask best practices
[Flask Hacks and Best Practices] <http://slides.skien.cc/flask-hacks-and-best-practices/>  
[Organizing your project - Flask 1.0 doc] <http://exploreflask.com/en/latest/organizing.html>  
[How to Structure Large Flask Applications] <https://www.digitalocean.com/community/tutorials/how-to-structure-large-flask-applications>

## 중요한 개념들
- Template rendering 시 Jinja2의 이스케이핑 방식 숙지, templates와 static 디렉토리 관리
- request data의 컨트롤(기본값, 타입, args와 form의 차이 등)
- 미들웨어와 werkzeug의 environ -> request wrapping
- app 객체의 데코레이터들을 통한 로깅
- ORM에 기반한 데이터베이스 모델링
- JWT, OAuth 등을 통한 토큰 기반 사용자 인증
- Swagger를 통한 API 문서화
- Blueprint를 이용한 모듈별 협업
- app.config와 g 객체

## Useful Packages
- Flask-restful
- Flask-restful-swagger
- Flasgger
- Flask-JWT
- Flask-CORS
- Flask-SocketIO

## 삽질하거나 막혔던 부분
### flask-restful의 리소스에서 jsonify를 사용하며 발생하는 이스케이핑 문제

Flask 객체의 route() 데코레이터는 딕셔너리나 리스트를 그대로 리턴하면 TypeError가 발생해서 대체적으로 flask의 jsonify로 문자열화 시켜준다. flask-restful이 수행하는 리스트와 딕셔너리의 자동 jsonify 처리 과정을 몰랐던 탓에 jsonify가 중첩되며 이스케이핑 문제가 발생했다.

route() 데코레이터 : 리스트나 딕셔너리 리턴 시 jsonify 사용  
flask-restful의 API : 리스트나 딕셔너리는 그대로 리턴

### Flask-restful에서 empty response 과정의 문제

기본 Flask 라우팅의 경우 ''를 리턴하면 자동으로 response body를 비워주는데 비해, Flask-restful에서는 아주 사실적으로 response가 처리되어 큰따옴표("")로 response된다. 이렇게 응답할 경우 Retrofit에서 Call<Void>로 설정된 콜백이 제대로 먹히지 않는다.

Flask-restful에서 ''를 리턴하면 ""로, None을 리턴하면 null로 반환된다. 이를 해결하기 위해선 Flask의 wrapper 클래스인 Response를 사용하면 된다.

    from flask import Response
    from flask_restful import Resource

    class Test(Resource):
        def get(self):
            return Response('', 200)


### g 객체의 'RuntimeError: Working outside of application context.'

Flask의 글로벌 객체인 g는 각각의 request thread에서만 값이 유효한 '스레드 로컬 변수'다. request context가 유지되고 있는 상태에서 g에 접근해야 RuntimeError를 피할 수 있다.

추가적으로 스레드 로컬 변수라는 특징 덕분에 사용자의 요청이 동시에 들어오더라도 각각의 request 내에서만 g 객체가 유효하기 때문에 동시접근에 대한 처리를 고민하지 않아도 된다.

### Flask-JWT의 /auth 자동 라우팅

Flask-JWT가 자동적으로 POST /auth라는 url rule을 가지는 라우팅을 진행한다는 점을 몰라서 막혔었다. 요청 데이터들은 authenticate handler 함수에 있는 2개 인자에 순서대로 전달된다.
    
    def authenticate(username, password):
        pass
    
    
### Flask-JWT의 url rule과 username key, password key가 고정된게 맘에 안들었다

토큰을 얻기 위해 /auth에 JSON 데이터로 요청을 보내는데, default 상태에선 항상 이런 형태여야 했다.

    POST /auth
    {
        "username": "planb",
        "password": "pw"
    }

key가 username과 password라는 점도 맘에 안들었고, url rule이 /auth라는 점도 맘에 안들었다. 구글링을 꽤 많이 했는데 해결을 못해서 flask-jwt 패키지를 직접 뜯어 봤는데 __init__.py에서 아래의 코드가 보였다.

    def init_app(self, app):
    for k, v in CONFIG_DEFAULTS.items():
        app.config.setdefault(k, v)

    app.config.setdefault('JWT_SECRET_KEY', app.config['SECRET_KEY'])
    auth_url_rule = app.config.get('JWT_AUTH_URL_RULE', None)

앱의 config에 기본값으로 config들을 채우고 있었다. for문으로 iteration하는 CONFIG_DEFAULTS를 확인해 보니 이렇게 생겼었다.

    CONFIG_DEFAULTS = {
        'JWT_DEFAULT_REALM': 'Login Required',
        'JWT_AUTH_URL_RULE': '/auth',
        'JWT_AUTH_ENDPOINT': 'jwt',
        'JWT_AUTH_USERNAME_KEY': 'username',
        'JWT_AUTH_PASSWORD_KEY': 'password',
        'JWT_ALGORITHM': 'HS256',
        'JWT_LEEWAY': timedelta(seconds=10),
        'JWT_AUTH_HEADER_PREFIX': 'JWT',
        'JWT_EXPIRATION_DELTA': timedelta(seconds=300),
        'JWT_NOT_BEFORE_DELTA': timedelta(seconds=0),
        'JWT_VERIFY_CLAIMS': ['signature', 'exp', 'nbf', 'iat'],
        'JWT_REQUIRED_CLAIMS': ['exp', 'iat', 'nbf']
    }

결론적으로 app.config를 통해 위의 JWT_AUTH_USERNAME_KEY와 JWT_AUTH_PASSWORD_KEY 등을 바꿔주면 되는 것이었다. 그냥 이렇게 시간낭비 하지 말고 Flask-JWT-Extended 쓰자.

### Swagger에서 API 문서를 불러오지 못하는 문제

결론부터 말하면 CORS 문제였다. flask-cors로 문제를 해결할 수 있었다.

    from flask import Flask
    from flask_cors import CORS

    app = Flask(__name__)
    CORS(app)

## Flask 서버 구조에 대한 개인적인 견해
- Blueprint와 Flask-restful을 활용해 체계적으로 분리된 API
- Swagger 등의 API 프레임워크를 이용한 코드 단에서의 API 스펙 정리
- SQLAlchemy, MongoEngine 등을 이용한 어플리케이션 단의 ORM/ODM
- Flask-JWT를 통한 토큰 기반 사용자 인증
- Flask 객체의 데코레이터 또는 미들웨어를 통한 헤더 설정과 로깅

## Keywords
### Flask
- Flask
- app.run
- app.config
- @app.route
- @app.errorhandler
- @app.before_first_request, before_request, after_request, teardown_request, teardown_appcontext
- request.args, request.form, request.json, request.values, request.files
- current_app
- g
- Blueprint
- redirect, url_for
- jsonify
- render_templates
- make_response, Response
- abort
- session
- logging, logging.handlers
- test_client
- Middleware
