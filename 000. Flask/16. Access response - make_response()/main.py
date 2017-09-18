from flask import Flask, make_response
# make_response() 함수를 통해 response 객체를 만들 수 있다

app = Flask(__name__)


@app.route('/')
def index():
    response = make_response('Body data')
    # response 객체 얻기. 함수엔 반환할 body data를 넣어 준다
    # 가변 인자지만 처음 으로 전달한 값이 담긴다

    # response 객체에선 많은 것들을 건드릴 수 있다
    # 대표적으로 헤더, 쿠키가 있는데 쿠키는 나중에 하려고 하니까 헤더만 써보자

    # 그냥 딕셔너리 쓰는거랑 똑같다
    response.headers['Something'] = 'Value'

    return response

app.run(debug=True)
