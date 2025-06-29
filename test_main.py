import unittest
from datetime import datetime
from main import DataManager, Exercise, Food

class TestDataManager(unittest.TestCase):
    def setUp(self):
        # Test dosyası ile çalış, gerçek veriyi etkileme
        self.data_manager = DataManager(data_file="test_exercise_data.json")
        self.data_manager.reset_all()

    def tearDown(self):
        import os
        if os.path.exists("test_exercise_data.json"):
            os.remove("test_exercise_data.json")

    def test_add_exercise(self):
        exercise = Exercise("Test Exercise", 30, 200, "01/01/2025", "12:00")
        self.data_manager.add_exercise(exercise)
        exercises = self.data_manager.get_exercises()
        self.assertEqual(len(exercises), 1)
        self.assertEqual(exercises[0].name, "Test Exercise")
        self.assertEqual(self.data_manager.get_total_calories_burned(), 200)

    def test_add_food(self):
        food = Food("Test Food", 500, "01/01/2025", "12:30")
        self.data_manager.add_food(food)
        foods = self.data_manager.get_food_intake()
        self.assertEqual(len(foods), 1)
        self.assertEqual(foods[0].name, "Test Food")
        self.assertEqual(self.data_manager.get_total_calories_intake(), 500)

    def test_clear_exercises(self):
        exercise = Exercise("Test", 10, 100, "01/01/2025", "13:00")
        self.data_manager.add_exercise(exercise)
        self.data_manager.clear_exercises()
        self.assertEqual(len(self.data_manager.get_exercises()), 0)
        self.assertEqual(self.data_manager.get_total_calories_burned(), 0)

    def test_clear_food(self):
        food = Food("Test", 150, "01/01/2025", "13:30")
        self.data_manager.add_food(food)
        self.data_manager.clear_food()
        self.assertEqual(len(self.data_manager.get_food_intake()), 0)
        self.assertEqual(self.data_manager.get_total_calories_intake(), 0)

    def test_reset_all(self):
        self.data_manager.add_exercise(Exercise("Ex", 5, 50, "01/01/2025", "14:00"))
        self.data_manager.add_food(Food("Fd", 100, "01/01/2025", "14:05"))
        self.data_manager.reset_all()
        self.assertEqual(len(self.data_manager.get_exercises()), 0)
        self.assertEqual(len(self.data_manager.get_food_intake()), 0)
        self.assertEqual(self.data_manager.get_total_calories_burned(), 0)
        self.assertEqual(self.data_manager.get_total_calories_intake(), 0)

if __name__ == "__main__":
    unittest.main()
