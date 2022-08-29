from msilib.schema import SelfReg
import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        # self.database_path = f"postgresql://student:student@localhost:5432/{self.database_name}"
        setup_db(self.app, self.database_path)
        self.new_question = {
            "questionWhich is the only team to play in every soccer World Cup tournament?": "Brazil",
             "category": "6", "difficult": 3
            }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_of_categories'])
        self.assertTrue(len(data['categories']))

    # def test_get_categories_error(self):

    #     res = self.client().get("/categories")
    #     data = json.loads(res.data)

    #     self.assertNotEqual(res.status_code,200)
    #     self.assertNotEqual(data['success'],True)
    #     self.assertEqualFalse(data['total_of_categories'])
    #     self.assertEqualFalse(len(data['categories']))



    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_of_questions"])
        self.assertTrue(len(data["questions"]))

    def test_empty_questions_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000",json={"category":4})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"],[])
        


    def test_get_specific_question(self):
        res = self.client().get("/detail/2")
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 2).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(question.format()['question'])
        self.assertTrue(data['total_questions'])


    def test_404_get_specific_question(self):
        res=self.client().get("/detail/1")
        data=json.loads(res.data)
        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')

    def test_delete_question(self):
        res=self.client().delete("/delete_question/10")
        question = Question.query.filter(Question.id == 10).one_or_none()
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data["deleted_question"],10)
        self.assertTrue(data["total_of_questions"])
        self.assertEqual(question, None)

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete("/delete_question/1000")
        data = json.loads(res.data)
   
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")


    def test_create_new_question(self):
        res = self.client().post("/create_question", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created_question"])
        self.assertTrue(len(data["questions"]))

    def test_404_if_question_creation_not_allowed(self):
        res = self.client().post("/create_question/45", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")
    


    def test_get_question_search_with_results(self):
        res = self.client().post("/searched_questions", json={"question": "title"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_of _searched_question"])
        self.assertTrue(len(data["questions"]))

    def test_get_question_search_without_results(self):
        res = self.client().post("/searched_questions", json={"question": "thi is"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_get_question_based_category(self):
        res = self.client().get("/categories/4/questions")
        data = json.loads(res.data)
        question_based_category=Question.query.filter(Question.category==str(4)).all()
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])
        self.assertEqual(data['total_of _searched_question'],len(question_based_category))
        self.assertTrue(data['current_category'])


    def test_404_get_question_based_category(self):
        res = self.client().get("/categories/100/questions")
        data = json.loads(res.data)
        question_based_category=Question.query.filter(Question.category==str(100)).all()
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'resource not found')


    def test_get_quizzes(self):
        res = self.client().post("/quizzes",json={"category":5, "previous_questions":[11,12,13]})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])
        self.assertTrue(data['previous_questions'])
        self.assertTrue(data['quiz_category'])
    def test_422_get_quizzes(self):
        res = self.client().post("/quizzes",json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],"unprocessable")








# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()