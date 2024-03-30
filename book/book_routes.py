from book import app,db
from flask_restx import Api,Resource,fields
from schemas.book_validator import BookValidator
from flask import request
from book.book_model import Book
from flask import g 
from flask_jwt_extended.exceptions import JWTDecodeError
from core.utils import authorize_user
from schemas.book_validator import BookValidator
from flask import request
from book.book_model import Book
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging


api=Api(app=app, title='Book Api', security='apiKey',
        authorizations={
            'apiKey':{
                'type':'apiKey',
                'in':'header',
                'required':True,
                'name':'Authorization'
            }
        }, doc="/docs")
limiter = Limiter(get_remote_address,app=app,default_limits=["200 per day","50 per day"])

@api.route('/addbook')
class AddingBookApi(Resource):
    method_decorators=[authorize_user]

    @api.doc(headers={"Authorization":"token for adding books"},
                body=api.model('adding book',{"title":fields.String(),
                                        "author":fields.String(),"price":fields.Integer(),
                                        "quantity":fields.Integer()}))
    @limiter.limit("20 per second")
    def post(self):
        """
    Endpoint for adding a book.

    This endpoint allows a superuser to add a new book to the system.
    If the authenticated user is not a superuser, it returns an error message with an HTTP status code of 403 (Forbidden).
    If the request is successful and the book is added, it returns a success message along with the added book data and an HTTP status code of 201 (Created).
    If the authentication token is invalid, it returns an error message with an HTTP status code of 401 (Unauthorized).
    If an unexpected error occurs during the process, it logs the error and returns an error message with an HTTP status code of 400 (Bad Request).

    Request Body:
        - title (str): The title of the book to be added.
        - author (str): The author of the book to be added.
        - other attributes...

    Returns:
        - dict: A dictionary containing a message indicating the result of the operation,
                the added book data, and an HTTP status code.
                Example (success):
                {
                    "message": "Book added successfully",
                    "data": {...},  # Book data in JSON format
                    "status": 201
                }
                Example (access denied):
                {
                    "message": "Access denied! You cannot perform this operation",
                    "status": 403
                }

    Raises:
        - 401 Unauthorized: If the authentication token is invalid.
        - 400 Bad Request: If an unexpected error occurs during the process.
    """
        try:
            if not g.user['is_superuser']:
                return {"message": "Access denied! You cannot perform this operation", "status": 403}, 403
            data = request.json
            data['user_id']=g.user['user_id']
            serializer=BookValidator(**data)
            data=serializer.model_dump()
            book=Book(**data)
            db.session.add(book)
            db.session.commit()
            return {"message":"Book added successfully","data":book.to_json,"status":201},201
        except JWTDecodeError as e:
            app.logger.exception(e,exc_info=False)
            return {"message":"Invalid Token","status":401},401
        except Exception as e:
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status code":400},400
        
@api.route('/getbook')
class RetreivingBookApi(Resource):

    @api.doc(headers={"Authorization":"token for retreiving book data"})
    @limiter.limit("20 per second")
    def get(self,*args,**kwargs):
        """
    Endpoint for retrieving all books.

    This endpoint retrieves all books from the database.
    If no books are found, it returns an error message with an HTTP status code of 400 (Bad Request).
    If books are retrieved successfully, it returns a success message along with the retrieved book data
    in a list format and an HTTP status code of 200 (OK).
    If an unexpected error occurs during the process, it logs the error and returns an error message
    with an HTTP status code of 500 (Internal Server Error).

    Returns:
        - dict: A dictionary containing a message indicating the result of the operation,
                the retrieved book data, and an HTTP status code.
                Example (success):
                {
                    "message": "Retrieved successfully",
                    "data": [...],  # List of book data in JSON format
                    "status": 200
                }
                Example (books not found):
                {
                    "message": "Book not found",
                    "status": 400
                }

    Raises:
        - 500 Internal Server Error: If an unexpected error occurs during the process.
    """
        try:
            books=Book.query.all()
            if not books:
                return {"message":"Book not found","status":400},400
            return {"msg":"retrieved successfully","data":[book.to_json for book in books]}
        except Exception as e:
            app.logger.exception(e,exc_info=False)
            return {"message":str(e),"status":500},500
        
@api.route('/deletebook')
class DeletingBookApi(Resource):
    method_decorators=[authorize_user]
    
    @api.doc(params={"book_id":"The id of the book that has to be deleted"},headers={"Authorization":"token for deleting books"})
    @limiter.limit("20 per second")
    def delete(self, *args, **kwargs):
        """
    Endpoint for deleting a book.

    This endpoint allows a superuser to delete a book from the system.
    If the authenticated user is not a superuser, it returns an error message with an HTTP status code of 403 (Forbidden).
    If no book ID is provided, it returns an error message with an HTTP status code of 400 (Bad Request).
    If the specified book ID does not exist, it returns an error message with an HTTP status code of 404 (Not Found).
    If the book is deleted successfully, it returns a success message with an HTTP status code of 204 (No Content).
    If an unexpected error occurs during the process, it logs the error and returns an error message
    with an HTTP status code of 500 (Internal Server Error).

    Query Parameters:
        - book_id (str): The ID of the book to be deleted.

    Returns:
        - dict: A dictionary containing a message indicating the result of the operation and an HTTP status code.
                Example (success):
                {
                    "message": "Book deleted successfully",
                    "status": 204
                }
                Example (access denied):
                {
                    "message": "Access denied! You cannot perform this operation",
                    "status": 403
                }
                Example (book ID required):
                {
                    "message": "Book ID is required to perform this operation",
                    "status": 400
                }

    Raises:
        - 404 Not Found: If the specified book ID does not exist.
        - 500 Internal Server Error: If an unexpected error occurs during the process.
    """
        try:
            if not g.user['is_superuser']:
                return {"message": "Access denied! You cannot perform this operation", "status": 403}, 403
            book_id = request.args.get('book_id')
            if not book_id:
                return {"message": "Book ID is required to perform this operation", "status": 400}, 400
            book = Book.query.get(book_id)
            if not book:
                return {"message": "Book not found", "status": 404}, 404
            db.session.delete(book)
            db.session.commit()
            return {"message": "Book deleted successfully", "status": 204}, 204
        except Exception as e:
            app.logger.exception(e,exc_info=False)
            return {"message": str(e), "status": 500}, 500
        

    
@api.route('/updatebook')
class UpdatingbookApi(Resource):
    method_decorators=[authorize_user]
    @api.doc(headers={"Authorization":"token for updating books"},
                body=api.model('updating book',{"title":fields.String(),
                                                "author":fields.String(),
                                                "price":fields.Integer(),"quantity":fields.Integer()}))
    @limiter.limit("20 per second")
    def put(self, *args, **kwargs):
        """
    Endpoint for updating a book.

    This endpoint allows a superuser to update the details of a book in the system.
    If the authenticated user is not a superuser, it returns an error message with an HTTP status code of 403 (Forbidden).
    If no book title is provided, it returns an error message with an HTTP status code of 400 (Bad Request).
    If the specified book title does not exist, it returns an error message with an HTTP status code of 404 (Not Found).
    If the book is updated successfully, it returns a success message with an HTTP status code of 200 (OK).
    If an unexpected error occurs during the process, it logs the error and returns an error message
    with an HTTP status code of 500 (Internal Server Error).

    Request Body:
        - title (str): The title of the book to be updated.
        - author (str, optional): The updated author of the book.
        - price (float, optional): The updated price of the book.
        - quantity (int, optional): The updated quantity of the book.

    Returns:
        - dict: A dictionary containing a message indicating the result of the operation and an HTTP status code.
                Example (success):
                {
                    "message": "Book updated successfully",
                    "status": 200
                }
                Example (access denied):
                {
                    "message": "Access denied! You cannot perform this operation",
                    "status": 403
                }
                Example (book title required):
                {
                    "message": "Book title is required to perform this operation",
                    "status": 400
                }

    Raises:
        - 404 Not Found: If the specified book title does not exist.
        - 500 Internal Server Error: If an unexpected error occurs during the process.
    """
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
            app.logger.exception(e,exc_info=False)
            return {"message": str(e), "status": 500}, 500
        

@app.route('/getBook',methods=['GET'])
def get_book():
    book_id=request.args.get("book_id")
    if not book_id:
        return {"message":"Book not found","status":400},400
    book=Book.query.get(book_id)
    if not book:
        return {"message":"unable to fetch book data","status":400},400
    return {"message":"book_id fetched successfully","book_data":book.to_json,"status":200},200

@app.post('/validatebooks')
def validate_books(*args,**kwargs):
    try:
        data=request.json
        for id,quantity in data.items():
            book=Book.query.filter_by(book_id=id).first()
            if not book:
                return {"message":"Book is not found","status":404},404
            if book.quantity<quantity:
                return {"message":"Insufficient quantity","status":400},400
            return {"message":"All items are ready to order","status":200},200
    except Exception as e:
        app.logger.exception(e,exc_info=False)
        return {"message":str(e),"status":500}

@app.patch('/updatebooks')
def update_books(*args,**kwargs):
    try:
        data=request.json
        for id,quantity in data.items():
            book=Book.query.filter_by(book_id=id).first()
            book.quantity-=quantity
        db.session.commit()
        return {"message":"Book quantity updated successfully","status":200},200
    except Exception as e:
        app.logger.exception(e,exc_info=False)
        return {"message":str(e),"status":500},500
        
