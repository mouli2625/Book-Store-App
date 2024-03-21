from book import app,db
from flask_restx import Api,Resource,fields
# from flask import g 
from schemas.book_validator import BookValidator
from flask import request
from book.book_model import Book



api=Api(app=app, title='Book Api',security='apiKey', doc="/docs")

@api.route('/add')
class AddingBookApi(Resource):

    @api.expect(api.model('adding book',{"title":fields.String(),"author":fields.String(),"price":fields.Integer(),"quantity":fields.Integer()}))
    def post(self):
        try:
            serializer=BookValidator(**request.json)
            data=serializer.model_dump()
            book=Book(**data)
            db.session.add(book)
            db.session.commit()
            return {"message":"Book added successfully","data":book.json,"status":201},201
        except Exception as e:
            return {"message":str(e),"status code":400},400
