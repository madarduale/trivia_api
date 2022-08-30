# from crypt import methods
# from crypt import methods
from asyncio import QueueEmpty
from errno import ESTALE
from hashlib import new
import json
import os
from sre_parse import CATEGORIES
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=['GET'])
    def get_all_categories():
        categories=Category.query.all()
        # formatted_categories=[]
        # for category in categories:
        #     # formatted_categories.append(category)
        if len(categories)==0:
            abort(404)
        return jsonify({
            'success':True,
            'categories':{category.id:category.type for category in categories},
            'total_of_categories':len(categories)
        })




    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
 
    @app.route("/questions", methods=['GET'])
    def get_all_question_with_categories():
        questions_per_page=10
        questions = Question.query.all()
        categories=Category.query.all()
        page=request.args.get('page',1,type=int)
        start=(page-1)*questions_per_page
        end=start+questions_per_page
        formatted_questions=[]
 
        for question in questions:
            formatted_questions.append(question.format())
        
        for category in categories:
            if category.id==int(question.category):
                current_category=category.type
    
        return jsonify({
            'success':True,
            'questions':formatted_questions[start:end],
            'total_questions':len(questions),
            'categories':{category.id: category.type for category in categories},
            'current_category':current_category 
        })
        





    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/detail/<int:question_id>", methods=['GET'])
    def question_detail(question_id):
        question=Question.query.get(question_id)
        if question is not None:
            
            return jsonify({
                'success': True,
                'question': question.format(),
                'total_questions': len(question.query.all())
            })
        else:
            abort(404)
    



    @app.route("/questions/<int:question_id>", methods=['DELETE'])
    def delete_question(question_id):
        specific_question=Question.query.filter(Question.id==question_id).one_or_none()
        if specific_question is None: 
            abort(422)
        specific_question.delete()
        questions_per_page=10
        questions = Question.query.order_by(Question.id).all()
        page=request.args.get('page',1,type=int)
        start=(page-1)*questions_per_page
        end=start+questions_per_page
        formatted_questions=[]
        for question in questions:
            formatted_questions.append(question.format())
        return jsonify({ 
            'questions':formatted_questions[start:end],
            'success':True,
            'deleted_question':specific_question.id,    
            'total_questions':len(questions)

        })





  

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """


    @app.route("/questions",methods=['POST'])
    def create_question():
        body=request.get_json()
        # new_id=body.get("id",None)
        new_question=body.get("question",None)
        new_answer=body.get("answer",None)
        new_difficulty=body.get("difficulty", None)
        new_category=body.get("category", None)
        try:
            new_question=Question(question=new_question,answer=new_answer,category=new_category,difficulty=new_difficulty)
            new_question.insert()
           
            questions_per_page=10
            questions = Question.query.order_by(Question.id).all()
            page=request.args.get('page',1,type=int)
            start=(page-1)*questions_per_page
            end=start+questions_per_page
            formatted_questions=[]
           
            for question in questions:
                formatted_questions.append(question.format())
            return jsonify({
                'questions':formatted_questions[start:end],
                'success':True,
                'created_question':question.id,
                'total_questions':len(questions)

                })
            
        except:
            abort(422)  

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """


    @app.route("/questions/search", methods=['POST'])
    def search():
        body=request.get_json()
        search_Term=body.get("searchTerm",None)
        if search_Term:
            search_questions=Question.query.filter(Question.question.ilike(f'%{search_Term}%')).all() 
            formatted_questions=[]
            questions_per_page=10
        
            page=request.args.get('page',1,type=int)
            start=(page-1)*questions_per_page
            end=start+questions_per_page
            
            categories=Category.query.all()
            current_category=[]
            for searchquestion in search_questions:
                for catgory in categories:
                    if catgory.id==int(searchquestion.category):
                        current_category.append(catgory.type)
                formatted_questions.append(searchquestion.format())

            return jsonify({
                'success':True,
                'questions':formatted_questions[start:end],
                'total_questions':len(search_questions),
                'current_category':current_category

            })
        else:
            abort(404)
      


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions", methods=['GET'])
    def get_question_based_category(category_id):
        
        try:
            question_based_category=Question.query.filter(Question.category==str(category_id)).all()
            categories=Category.query.all()
        
            formatted_questions=[]
            questions_per_page=10
            page=request.args.get('page',1,type=int)
            start=(page-1)*questions_per_page
            end=start+questions_per_page
            if question_based_category: 
                for searchquestion in question_based_category:
                    formatted_questions.append(searchquestion.format())
                for category in categories:
                    if category.id==int(searchquestion.category):
                        current_category=category.type
                    
          

            return jsonify({
                'success':True,
                'questions':formatted_questions[start:end],
                'total_questions':len(question_based_category),
                'current_category':current_category
            })
        except:
            abort(404)
            
        




    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """


    @app.route("/quizzes", methods=['POST'])
    def quiz(): 




        try:
            body = request.get_json()
            category =body.get("quiz_category",None)
            previous_questions = body.get("previous_questions",None)
            
            available_questions=Question.query.filter_by(category=category['id']).filter(Question.id.notin_((previous_questions))).all()
            # available_questions=Question.query.filter(Category.id==category).filter(Question.id.notin_((previous_questions))).all()
               
            
            if len(available_questions) > 0:
                randomquestion=available_questions[random.randrange(0, len(available_questions))]
            else: None
      
            return jsonify({
                'success':True,
                'question':randomquestion.format(),

            })
        except:
            abort(422)

        
           try:
                body = request.get_json()
                category =body.get("quiz_category",None)
                previous_questions = body.get("previous_questions",None)
            
                available_questions=Question.query.filter_by(category=category['id']).filter(Question.id.notin_((previous_questions))).all()
               
            
                if len(available_questions) > 0:
                      randomquestion=available_questions[random.randrange(0, len(available_questions))]
                else: None
           
                 return jsonify({
                        'success':True,
                        'question':randomquestion.format(),
               
                        })
           except:
                  abort(422)




       


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )


    return app

