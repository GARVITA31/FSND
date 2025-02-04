import json
import os
import re
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
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods','GET, POST, PATCH, DELETE, OPTIONS')
    return response

  @app.route('/')
  def hello():
    return jsonify({'message': 'Hello There!!!'})

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories = Category.query.order_by(Category.type).all()
    if len(categories) == 0:
      not_found(404)
    return jsonify({
      'success': True,
      'categories': {category.id: category.type for category in categories}
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    allQuestions = Question.query.order_by(Question.id).all()
    page = request.args.get('page', 1, type = int)
    start = (page - 1) * 10
    end = start + 10
    selectedQuestions = [question.format() for question in allQuestions]
    pagedQuestions = selectedQuestions[start:end]

    categories = Category.query.order_by(Category.type).all()
    if len(pagedQuestions) != 0:
      return jsonify({
        'success': True,
        'questions': pagedQuestions,
        'total_questions': len(allQuestions),
        'current_category': None,
        'categories': {category.id: category.type for category in categories}
      })
    else:
      abort(404)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()
      return jsonify({
        'success': True,
        'deleted_question': question_id
      })
    except:
      abort(404)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():
    body = request.get_json()
    if ('question' in body and 'answer' in body and 'category' in body and 'difficulty' in body):
      new_question = body.get('question')
      new_answer = body.get('answer')
      new_category = body.get('category')
      new_difficulty = body.get('difficulty')
      try:
        question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
        question.insert()
        return jsonify({
          'success': True,
          'added_question': question.id
        })
      except:
        abort(404)
    else:
      abort(404)


  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  @app.route('/questions/search', methods = ['POST'])
  def search_questions():
    body = request.get_json()
    search_term = body.get('searchTerm')
    if search_term:
      search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      if len(search_results) == 0:
        abort(404)
      else:
        return jsonify({
          'success': True,
          'questions': [question.format() for question in search_results],
        })
    else:
      abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods = ['GET'])
  def get_questions_by_category(category_id):
    try:
      questions = Question.query.filter(Question.category == str(category_id)).all()
      if len(questions) != 0:
        return jsonify({
            'success': True,
            'questions': [question.format() for question in questions],
        })
      else:
        abort(404)
    except:
      abort(404)


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods = ['POST'])
  def play_quiz():
    try:
      body = request.get_json()
      if('previous_questions' in body and 'quiz_category' in body):
        category = body.get('quiz_category')
        prev_questions = body.get('previous_questions')

        if category['id'] == 0:
          available_questions = Question.query.filter(Question.id.notin_(prev_questions)).all()
        else:
          available_questions = Question.query.filter_by(category = category['id']).filter(Question.id.notin_(prev_questions)).all()
        
        if len(available_questions) > 0:
          next_question = available_questions[random.randrange(0, len(available_questions))].format()
        else:
          next_question = None

        return jsonify({
          'success': True,
          'question': next_question
        })
      else:
        abort(404)
    except:
      abort(404)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource Not Found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable'
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad Request'
    }), 400

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': 'Method Not Allowed'
    }), 405
    
  return app

    