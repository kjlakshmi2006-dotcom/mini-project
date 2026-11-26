import unittest
import json
from app import app
from database.db import init_db
from database.seed_data import seed_database
from services.auth_service import register_user, authenticate_user
from services.ai_classifier import classify_learning_level
from services.quiz_service import (
    get_diagnostic_questions, evaluate_diagnostic_quiz,
    get_topic_questions, evaluate_topic_quiz
)
from services.adaptive_engine import get_adaptive_material, get_curriculum_status
from services.report_service import get_student_performance_data

class TestAdaptLearn(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()
        cls.client = app.test_client()
        app.config["TESTING"] = True

    def test_01_classification_boundaries(self):
        # Basic: < 40%
        self.assertEqual(classify_learning_level(0), "basic")
        self.assertEqual(classify_learning_level(30), "basic")
        self.assertEqual(classify_learning_level(39.9), "basic")

        # Intermediate: 40% - 70%
        self.assertEqual(classify_learning_level(40), "intermediate")
        self.assertEqual(classify_learning_level(55), "intermediate")
        self.assertEqual(classify_learning_level(70), "intermediate")

        # Advanced: > 70%
        self.assertEqual(classify_learning_level(70.1), "advanced")
        self.assertEqual(classify_learning_level(90), "advanced")
        self.assertEqual(classify_learning_level(100), "advanced")
        print("[TEST PASS] Learning level boundary tests verified.")

    def test_02_student_registration_and_auth(self):
        # Register student
        ok, res = register_user("test_student", "student@test.com", "password123")
        self.assertTrue(ok or "already" in str(res).lower())

        # Authenticate
        auth_ok, user = authenticate_user("test_student", "password123")
        self.assertTrue(auth_ok)
        self.assertEqual(user["username"], "test_student")
        print("[TEST PASS] Student registration & authentication verified.")

    def test_03_diagnostic_quiz_flow(self):
        auth_ok, user = authenticate_user("test_student", "password123")
        self.assertTrue(auth_ok)
        uid = user["id"]

        questions = get_diagnostic_questions()
        self.assertEqual(len(questions), 10)

        # Simulate 2 correct answers (20% -> basic level)
        simulated_basic_answers = {
            str(questions[0]["id"]): "B", # Correct
            str(questions[1]["id"]): "C", # Correct
            str(questions[2]["id"]): "A", # Incorrect
        }
        res_basic = evaluate_diagnostic_quiz(uid, simulated_basic_answers)
        self.assertEqual(res_basic["correct_count"], 2)
        self.assertEqual(res_basic["score_percentage"], 20.0)
        self.assertEqual(res_basic["assigned_level"], "basic")

        # Simulate 5 correct answers (50% -> intermediate level)
        simulated_inter_answers = {
            str(questions[0]["id"]): "B",
            str(questions[1]["id"]): "C",
            str(questions[2]["id"]): "B",
            str(questions[3]["id"]): "B",
            str(questions[4]["id"]): "B",
        }
        res_inter = evaluate_diagnostic_quiz(uid, simulated_inter_answers)
        self.assertEqual(res_inter["correct_count"], 5)
        self.assertEqual(res_inter["score_percentage"], 50.0)
        self.assertEqual(res_inter["assigned_level"], "intermediate")

        # Simulate 8 correct answers (80% -> advanced level)
        simulated_adv_answers = {
            str(questions[0]["id"]): "B",
            str(questions[1]["id"]): "C",
            str(questions[2]["id"]): "B",
            str(questions[3]["id"]): "B",
            str(questions[4]["id"]): "B",
            str(questions[5]["id"]): "C",
            str(questions[6]["id"]): "A",
            str(questions[7]["id"]): "A",
        }
        res_adv = evaluate_diagnostic_quiz(uid, simulated_adv_answers)
        self.assertEqual(res_adv["correct_count"], 8)
        self.assertEqual(res_adv["score_percentage"], 80.0)
        self.assertEqual(res_adv["assigned_level"], "advanced")
        print("[TEST PASS] 10-Question Diagnostic Quiz evaluation & dynamic tier assignment verified.")

    def test_04_adaptive_content_delivery(self):
        auth_ok, user = authenticate_user("test_student", "password123")
        uid = user["id"]

        # User was set to 'advanced' from previous test
        material_adv = get_adaptive_material(uid, topic_id=1)
        self.assertEqual(material_adv["user_level"], "advanced")
        self.assertEqual(material_adv["material"]["level_tier"], "advanced")
        self.assertIn("Advanced Python", material_adv["material"]["title"])

        print("[TEST PASS] Adaptive content resolution (delivering tier-matched short notes & clips) verified.")

    def test_05_topic_micro_assessment_and_progression(self):
        auth_ok, user = authenticate_user("test_student", "password123")
        uid = user["id"]

        topic_q = get_topic_questions(1)
        self.assertTrue(len(topic_q) >= 3)

        # Submit answers (all correct -> 100% -> passed)
        answers = {
            str(topic_q[0]["id"]): "B",
            str(topic_q[1]["id"]): "B",
            str(topic_q[2]["id"]): "C"
        }
        res = evaluate_topic_quiz(uid, 1, answers)
        self.assertTrue(res["passed"])
        self.assertEqual(res["status"], "completed")
        self.assertIsNotNone(res["next_topic"])
        self.assertEqual(res["next_topic"]["sequence_order"], 2)

        curriculum = get_curriculum_status(uid, 1)
        self.assertEqual(curriculum["completed_topics"], 1)
        print("[TEST PASS] Topic micro-assessment, mastery tracking & next topic recommendation verified.")

    def test_06_performance_analytics_data(self):
        auth_ok, user = authenticate_user("test_student", "password123")
        uid = user["id"]

        perf = get_student_performance_data(uid)
        self.assertEqual(len(perf["chart_data"]["radar"]["labels"]), 5)
        self.assertTrue(len(perf["attempts_history"]) >= 2)
        self.assertIsNotNone(perf["latest_report"])
        print("[TEST PASS] Performance reports & Chart.js data aggregation verified.")

    def test_07_http_routes(self):
        # Test HTTP endpoints with session
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "test_student"
            sess["learning_level"] = "advanced"

        res_dash = self.client.get("/dashboard")
        self.assertEqual(res_dash.status_code, 200)

        res_diag = self.client.get("/quiz/diagnostic")
        self.assertEqual(res_diag.status_code, 200)

        res_learn = self.client.get("/learn/1")
        self.assertEqual(res_learn.status_code, 200)

        res_reports = self.client.get("/reports")
        self.assertEqual(res_reports.status_code, 200)

        print("[TEST PASS] All Flask HTTP routes (dashboard, quiz, learn, reports) returned 200 OK.")

if __name__ == "__main__":
    unittest.main()
