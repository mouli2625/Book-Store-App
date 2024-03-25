from book import app,db
from flask_restx import Api,Resource,fields
from schemas.book_validator import BookValidator
from flask import request
from book.book_model import Book
from flask import g 
from flask_jwt_extended.exceptions import JWTDecodeError
from book.utils import authorize_user
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
            return {"message":"Book added successfully","data":book.to_json,"status":201},201
        except JWTDecodeError:
            return {"message":"Invalid Token","status":401},401
        except Exception as e:
            return {"message":str(e),"status code":400},400
        
    # @api.expect(api.model('retreiving book data',{'userid':fields.Integer()}))
@api.route('/getbook')
class RetreivingBookApi(Resource):

    def get(self,*args,**kwargs):
        try:
            books=Book.query.all()
            if not books:
                return {"message":"Book not found","status":400},400
            return {"msg":"retrieved successfully","data":[book.to_json for book in books]}
            
            
        except Exception as e:
            return {"message":str(e),"status":500},500
        
@api.route('/deletebook')
class DeletingBookApi(Resource):
    method_decorators=[authorize_user]
    
    @api.expect(api.model("Deleting book",{"title":fields.String()}))
    def delete(self, *args, **kwargs):
        try:
            if not g.user['is_superuser']:
                return {"message": "Access denied! You cannot perform this operation", "status": 403}, 403
            data = request.json
            book_title = data.get('title')
            if not book_title:
                return {"message": "Book title is required to perform this operation", "status": 400}, 400
            book = Book.query.filter_by(title=book_title).first()
            if not book:
                return {"message": "Book not found", "status": 404}, 404
            db.session.delete(book)
            db.session.commit()
            return {"message": "Book deleted successfully", "status": 204}, 204
        except Exception as e:
            return {"message": str(e), "status": 500}, 500
        

    
@api.route('/updatebook')
class UpdatingbookApi(Resource):
    method_decorators=[authorize_user]
    @api.expect(api.model("Updating book",{"title":fields.String(),"author":fields.String(),"quantity":fields.Integer,"price":fields.Integer}))
    def put(self, *args, **kwargs):
        try:
            if not g.user['is_superuser']:
                return {"message": "Access denied! You cannot perform this operation", "status": 403}, 403
            data = request.json
            book_title = data.get('title')
            if not book_title:
                return {"message": "Book title is required to perform this operation", "status": 400}, 400
            book = Book.query.filter_by(title=book_title).first()
            if not book:
                return {"message": "Book not found", "status": 404}, 404
            [setattr(book, key, data.get(key, getattr(book, key))) for key in ['author', 'price', 'quantity']]
            db.session.commit()
            return {"message": "Book updated successfully", "status": 200}, 200
        except Exception as e:
            return {"message": str(e), "status": 500}, 500
            return {"message":"Book added successfully","data":book.json,"status":201},201
        except Exception as e:
            return {"message":str(e),"status code":400},400
