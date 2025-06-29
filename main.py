import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
from abc import ABC, abstractmethod


class BaseRecord(ABC):
    def __init__(self, name, calories, date, timestamp):
        self.name = name
        self.calories = calories
        self.date = date
        self.timestamp = timestamp

    @abstractmethod
    def to_dict(self):
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data):
        pass

    @abstractmethod
    def get_type(self):
        pass

    def get_summary(self):
        return f"{self.timestamp} - {self.name}, {self.calories} calories"

class Exercise(BaseRecord):
    def __init__(self, name, duration, calories, date, timestamp):
        super().__init__(name, calories, date, timestamp)
        self.duration = duration

    def to_dict(self):
        return {
            "name": self.name,
            "duration": self.duration,
            "calories": self.calories,
            "date": self.date,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("name", ""),
            data.get("duration", 0),
            data.get("calories", 0),
            data.get("date", ""),
            data.get("timestamp", "")
        )

    def get_type(self):
        return "Exercise"

    def get_summary(self):
        return f"{self.timestamp} - {self.name}, {self.duration} min, {self.calories} calories"

class Food(BaseRecord):
    def __init__(self, name, calories, date, timestamp):
        super().__init__(name, calories, date, timestamp)

    def to_dict(self):
        return {
            "name": self.name,
            "calories": self.calories,
            "date": self.date,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("name", ""),
            data.get("calories", 0),
            data.get("date", ""),
            data.get("timestamp", "")
        )

    def get_type(self):
        return "Food"



class DataManager:
    def __init__(self, data_file="exercise_data.json"):
        self.data_file = data_file
        self.data = {
            "exercises": [],
            "food_intake": [],
            "total_calories_burned": 0,
            "total_calories_intake": 0,
            "current_date": datetime.now().strftime("%d/%m/%Y"),
            "target_calories": 2000,
            "activity_level": "Moderate"
        }
        self.load_data()

    def save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f)

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"Error loading data: {str(e)}")
                self.save_data()

    def get_exercises(self):
        return [Exercise.from_dict(item) for item in self.data.get("exercises", [])]

    def get_food_intake(self):
        return [Food.from_dict(item) for item in self.data.get("food_intake", [])]

    def add_exercise(self, exercise: Exercise):
        self.data["exercises"].append(exercise.to_dict())
        self.data["total_calories_burned"] += exercise.calories
        self.save_data()

    def add_food(self, food: Food):
        self.data["food_intake"].append(food.to_dict())
        self.data["total_calories_intake"] += food.calories
        self.save_data()

    def clear_exercises(self):
        self.data["exercises"] = []
        self.data["total_calories_burned"] = 0
        self.save_data()

    def clear_food(self):
        self.data["food_intake"] = []
        self.data["total_calories_intake"] = 0
        self.save_data()

    def reset_all(self):
        self.data["exercises"] = []
        self.data["food_intake"] = []
        self.data["total_calories_burned"] = 0
        self.data["total_calories_intake"] = 0
        self.save_data()

    def get_total_calories_burned(self):
        return self.data.get("total_calories_burned", 0)

    def get_total_calories_intake(self):
        return self.data.get("total_calories_intake", 0)

    def get_target_calories(self):
        return self.data.get("target_calories", 2000)

    def get_activity_level(self):
        return self.data.get("activity_level", "Moderate")

    def get_current_date(self):
        return self.data.get("current_date", datetime.now().strftime("%d/%m/%Y"))


class BaseFrame(ttk.Frame, ABC):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    @abstractmethod
    def create_widgets(self):
        pass

    def export_data(self):
        pass  


class ExerciseTracker(BaseFrame):
    def __init__(self, parent, controller):
        self.data_manager = DataManager()
        super().__init__(parent, controller)

    def create_widgets(self):
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.history_frame = ttk.Frame(self, padding="10")
        self.history_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.food_history_frame = ttk.Frame(self, padding="10")
        self.food_history_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
       
        ttk.Label(self.history_frame, text="Exercise History", font=('Arial', 14, 'bold')).pack(pady=10)
        self.history_list = tk.Listbox(self.history_frame, width=50, height=25)
        self.history_list.pack(fill=tk.BOTH, expand=True)
        ttk.Button(self.history_frame, text="Clear Exercise History", command=self.clear_history).pack(pady=10)
        ttk.Label(self.food_history_frame, text="Food History", font=('Arial', 14, 'bold')).pack(pady=10)
        self.food_history_list = tk.Listbox(self.food_history_frame, width=50, height=25)
        self.food_history_list.pack(fill=tk.BOTH, expand=True)
        ttk.Button(self.food_history_frame, text="Clear Food History", command=self.clear_food_history).pack(pady=10)
        ttk.Label(self.main_frame, text="Add Exercise", font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(self.main_frame, text="Exercise Name:").grid(row=1, column=0, sticky=tk.W)
        self.exercise_name = ttk.Entry(self.main_frame)
        self.exercise_name.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(self.main_frame, text="Duration (minutes):").grid(row=2, column=0, sticky=tk.W)
        self.duration = ttk.Entry(self.main_frame)
        self.duration.grid(row=2, column=1, padx=5, pady=5)
        ttk.Label(self.main_frame, text="Calories Burned:").grid(row=3, column=0, sticky=tk.W)
        self.calorie_burned = ttk.Entry(self.main_frame)
        self.calorie_burned.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(self.main_frame, text="Add Exercise", command=self.add_exercise).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Label(self.main_frame, text="Food Name:").grid(row=5, column=0, sticky=tk.W)
        self.food_name = ttk.Entry(self.main_frame)
        self.food_name.grid(row=5, column=1, padx=5, pady=5)
        ttk.Label(self.main_frame, text="Calories:").grid(row=6, column=0, sticky=tk.W)
        self.calorie_intake = ttk.Entry(self.main_frame)
        self.calorie_intake.grid(row=6, column=1, padx=5, pady=5)
        ttk.Button(self.main_frame, text="Add Food", command=self.add_calorie).grid(row=7, column=0, columnspan=2, pady=10)
        ttk.Label(self.main_frame, text="Total Calories", font=('Arial', 14, 'bold')).grid(row=8, column=0, columnspan=2, pady=10)
        self.total_calories_label = ttk.Label(self.main_frame, text="Total Calories Burned: 0")
        self.total_calories_label.grid(row=9, column=0, columnspan=2, pady=5)
        self.total_intake_label = ttk.Label(self.main_frame, text="Total Calories Intake: 0")
        self.total_intake_label.grid(row=10, column=0, columnspan=2, pady=5)
        self.net_calories_label = ttk.Label(self.main_frame, text="Net Calories: 0")
        self.net_calories_label.grid(row=11, column=0, columnspan=2, pady=5)
        self.target_progress = ttk.Progressbar(self.main_frame, orient='horizontal', length=200, mode='determinate')
        self.target_progress.grid(row=12, column=0, columnspan=2, pady=5)
        self.target_label = ttk.Label(self.main_frame, text="Target Progress: 0%")
        self.target_label.grid(row=13, column=0, columnspan=2, pady=5)
        ttk.Button(self.main_frame, text="Reset Total Calories", command=self.reset_calories).grid(row=14, column=0, columnspan=2, pady=10)
        self.date_label = ttk.Label(self.main_frame, text=f"Date: {datetime.now().strftime('%d/%m/%Y')}")
        self.date_label.grid(row=15, column=0, columnspan=2, pady=5)
        self.update_calories()
        self.update_history()

    def add_exercise(self):
        try:
            name = self.exercise_name.get().strip()
            duration_str = self.duration.get().strip()
            calories_str = self.calorie_burned.get().strip()
            if not name or not duration_str or not calories_str:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            try:
                duration = float(duration_str)
                calories = float(calories_str)
            except ValueError:
                messagebox.showerror("Error", "Duration and calories must be numbers")
                return
            if duration <= 0 or calories <= 0:
                messagebox.showerror("Error", "Duration and calories must be positive numbers")
                return
            exercise = Exercise(name, duration, calories, self.data_manager.get_current_date(), datetime.now().strftime("%H:%M"))
            self.data_manager.add_exercise(exercise)
            self.update_calories()
            self.update_history()
            self.exercise_name.delete(0, tk.END)
            self.duration.delete(0, tk.END)
            self.calorie_burned.delete(0, tk.END)
            messagebox.showinfo("Success", f"Exercise '{name}' added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def add_calorie(self):
        try:
            name = self.food_name.get().strip()
            calories_str = self.calorie_intake.get().strip()
            if not name or not calories_str:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            try:
                calories = float(calories_str)
            except ValueError:
                messagebox.showerror("Error", "Calories must be a number")
                return
            if calories <= 0:
                messagebox.showerror("Error", "Calories must be a positive number")
                return
            food = Food(name, calories, self.data_manager.get_current_date(), datetime.now().strftime("%H:%M"))
            self.data_manager.add_food(food)
            self.update_calories()
            self.update_history()
            self.food_name.delete(0, tk.END)
            self.calorie_intake.delete(0, tk.END)
            messagebox.showinfo("Success", f"Food '{name}' added successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def update_calories(self):
        total_burned = self.data_manager.get_total_calories_burned()
        total_intake = self.data_manager.get_total_calories_intake()
        self.total_calories_label.config(text=f"Total Calories Burned: {total_burned:.1f}")
        self.total_intake_label.config(text=f"Total Calories Intake: {total_intake:.1f}")
        net_calories = total_intake - total_burned
        self.net_calories_label.config(text=f"Net Calories: {net_calories:.1f}")
        progress = min(100, (total_burned / self.data_manager.get_target_calories()) * 100)
        self.target_progress['value'] = progress
        self.target_label.config(text=f"Target Progress: {progress:.1f}%")
        if progress >= 100:
            self.target_progress.configure(style='Green.Horizontal.TProgressbar')
        elif progress >= 75:
            self.target_progress.configure(style='Yellow.Horizontal.TProgressbar')
        else:
            self.target_progress.configure(style='Red.Horizontal.TProgressbar')

    def update_history(self):
        self.history_list.delete(0, tk.END)
        for exercise in reversed(self.data_manager.get_exercises()):
            entry = f"{exercise.timestamp} - {exercise.name}, {exercise.duration} min, {exercise.calories} calories"
            self.history_list.insert(tk.END, entry)
        self.food_history_list.delete(0, tk.END)
        for food in reversed(self.data_manager.get_food_intake()):
            entry = f"{food.timestamp} - {food.name}, {food.calories} calories"
            self.food_history_list.insert(tk.END, entry)

    def clear_history(self):
        self.data_manager.clear_exercises()
        self.update_calories()
        self.update_history()
        messagebox.showinfo("Success", "Exercise history cleared successfully!")

    def clear_food_history(self):
        self.data_manager.clear_food()
        self.update_calories()
        self.update_history()
        messagebox.showinfo("Success", "Food history cleared successfully!")

    def reset_calories(self):
        self.data_manager.reset_all()
        self.update_calories()
        self.update_history()
        messagebox.showinfo("Success", "All data has been reset successfully!")

    def export_data(self):
        try:
            filename = f"exercise_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w') as f:
                f.write("Type,Date,Time,Name,Duration,Calories\n")
                for item in self.data_manager.get_exercises():
                    f.write(f"Exercise,{item.date},{item.timestamp},{item.name},{item.duration},{item.calories}\n")
                for item in self.data_manager.get_food_intake():
                    f.write(f"Food,{item.date},{item.timestamp},{item.name},,{item.calories}\n")
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {str(e)}")


class BMICalculatorService:
    @staticmethod
    def calculate_bmi(height_cm, weight_kg):
        try:
            height = float(height_cm) / 100
            weight = float(weight_kg)
            bmi = weight / (height * height)
            return bmi
        except Exception:
            return None

    @staticmethod
    def get_bmi_category(bmi):
        if bmi is None:
            return "Invalid"
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal weight"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"

class BMICalculator(BaseFrame):
    def create_widgets(self):
        label = ttk.Label(self, text="BMI Calculator", font=('Arial', 16, 'bold'))
        label.pack(pady=10, padx=10)
        ttk.Label(self, text="Height (cm):").pack()
        self.height = ttk.Entry(self)
        self.height.pack()
        ttk.Label(self, text="Weight (kg):").pack()
        self.weight = ttk.Entry(self)
        self.weight.pack()
        self.result = ttk.Label(self, text="")
        self.result.pack(pady=10)
        ttk.Button(self, text="Calculate BMI", command=self.calculate_bmi).pack()

    def calculate_bmi(self):
        height_val = self.height.get()
        weight_val = self.weight.get()
        bmi = BMICalculatorService.calculate_bmi(height_val, weight_val)
        if bmi is None:
            self.result.config(text="Please enter valid numbers")
            return
        category = BMICalculatorService.get_bmi_category(bmi)
        self.result.config(text=f"BMI: {bmi:.1f} - {category}")


class CalorieCalculator(BaseFrame):
    def create_widgets(self):
        label = ttk.Label(self, text="Daily Calorie Needs Calculator", font=('Arial', 16, 'bold'))
        label.pack(pady=10, padx=10)
        ttk.Label(self, text="Age:").pack()
        self.age = ttk.Entry(self)
        self.age.pack()
        ttk.Label(self, text="Gender:").pack()
        self.gender = ttk.Combobox(self, values=["Male", "Female"])
        self.gender.pack()
        ttk.Label(self, text="Weight (kg):").pack()
        self.weight = ttk.Entry(self)
        self.weight.pack()
        ttk.Label(self, text="Height (cm):").pack()
        self.height = ttk.Entry(self)
        self.height.pack()
        ttk.Label(self, text="Activity Level:").pack()
        self.activity = ttk.Combobox(self, values=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"])
        self.activity.pack()
        self.result = ttk.Label(self, text="")
        self.result.pack(pady=10)
        ttk.Button(self, text="Calculate Daily Calories", command=self.calculate_calories).pack()

    def calculate_calories(self):
        try:
            age = int(self.age.get())
            weight = float(self.weight.get())
            height = float(self.height.get())
            gender = self.gender.get()
            activity = self.activity.get()
            if gender == "Male":
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            activity_multiplier = {
                "Sedentary": 1.2,
                "Lightly Active": 1.375,
                "Moderately Active": 1.55,
                "Very Active": 1.725,
                "Extra Active": 1.9
            }.get(activity, 1.2)
            daily_calories = bmr * activity_multiplier
            self.result.config(text=f"Daily Calorie Needs: {daily_calories:.0f} calories")
        except ValueError:
            self.result.config(text="Please enter valid numbers")


class MainApplication(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Health & Fitness Tracker")
        self.geometry("1000x800")
        self.configure(bg='#f0f0f0')
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        menubar = tk.Menu(container, font=('Arial', 12))
        nav_menu = tk.Menu(menubar, tearoff=0, font=('Arial', 12))
        nav_menu.add_command(label="Exercise Tracker", command=lambda: self.show_frame("ExerciseTracker"), font=('Arial', 12))
        nav_menu.add_command(label="BMI Calculator", command=lambda: self.show_frame("BMICalculator"), font=('Arial', 12))
        nav_menu.add_command(label="Calorie Calculator", command=lambda: self.show_frame("CalorieCalculator"), font=('Arial', 12))
        menubar.add_cascade(label="Navigation", menu=nav_menu, font=('Arial', 12))
        self.config(menu=menubar)
        style = ttk.Style()
        style.configure('TMenubutton', font=('Arial', 12))
        style.configure('TButton', font=('Arial', 11))
        style.configure('TLabel', font=('Arial', 11))
        self.frames = {}
        for F in (ExerciseTracker, BMICalculator, CalorieCalculator):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame("ExerciseTracker")

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()




    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.history_frame = ttk.Frame(self, padding="10")
        self.history_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.food_history_frame = ttk.Frame(self, padding="10")
        self.food_history_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root = controller
        
        self.data_file = "exercise_data.json"
        self.exercises = []
        self.food_intake = []
        self.total_calories_burned = 0
        self.total_calories_intake = 0
        self.history = []
        self.food_history = []
        self.current_date = datetime.now().strftime("%d/%m/%Y")
        
        self.target_calories = 2000
        self.activity_level = "Moderate"
        
        self.create_widgets()
        self.load_data()
        self.update_calories()
        self.update_history()
        
 

    def create_widgets(self):
        ttk.Label(self.history_frame, text="Exercise History", font=('Arial', 14, 'bold')).pack(pady=10)
        
        self.history_list = tk.Listbox(self.history_frame, width=50, height=25)
        self.history_list.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(self.history_frame, text="Clear Exercise History", command=self.clear_history).pack(pady=10)

        ttk.Label(self.food_history_frame, text="Food History", font=('Arial', 14, 'bold')).pack(pady=10)
        
        self.food_history_list = tk.Listbox(self.food_history_frame, width=50, height=25)
        self.food_history_list.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(self.food_history_frame, text="Clear Food History", command=self.clear_food_history).pack(pady=10)

        ttk.Label(self.main_frame, text="Add Exercise", font=('Arial', 14, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(self.main_frame, text="Exercise Name:").grid(row=1, column=0, sticky=tk.W)
        self.exercise_name = ttk.Entry(self.main_frame)
        self.exercise_name.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.main_frame, text="Duration (minutes):").grid(row=2, column=0, sticky=tk.W)
        self.duration = ttk.Entry(self.main_frame)
        self.duration.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.main_frame, text="Calories Burned:").grid(row=3, column=0, sticky=tk.W)
        self.calorie_burned = ttk.Entry(self.main_frame)
        self.calorie_burned.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(self.main_frame, text="Add Exercise", command=self.add_exercise).grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Label(self.main_frame, text="Food Name:").grid(row=5, column=0, sticky=tk.W)
        self.food_name = ttk.Entry(self.main_frame)
        self.food_name.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(self.main_frame, text="Calories:").grid(row=6, column=0, sticky=tk.W)
        self.calorie_intake = ttk.Entry(self.main_frame)
        self.calorie_intake.grid(row=6, column=1, padx=5, pady=5)

        ttk.Button(self.main_frame, text="Add Food", command=self.add_calorie).grid(row=7, column=0, columnspan=2, pady=10)
        
        ttk.Label(self.main_frame, text="Total Calories", font=('Arial', 14, 'bold')).grid(row=8, column=0, columnspan=2, pady=10)
        
        self.total_calories_label = ttk.Label(self.main_frame, text="Total Calories Burned: 0")
        self.total_calories_label.grid(row=9, column=0, columnspan=2, pady=5)
        
        self.total_intake_label = ttk.Label(self.main_frame, text="Total Calories Intake: 0")
        self.total_intake_label.grid(row=10, column=0, columnspan=2, pady=5)
        
        self.net_calories_label = ttk.Label(self.main_frame, text="Net Calories: 0")
        self.net_calories_label.grid(row=11, column=0, columnspan=2, pady=5)
        
        self.target_progress = ttk.Progressbar(self.main_frame, orient='horizontal', length=200, mode='determinate')
        self.target_progress.grid(row=12, column=0, columnspan=2, pady=5)
        
        self.target_label = ttk.Label(self.main_frame, text="Target Progress: 0%")
        self.target_label.grid(row=13, column=0, columnspan=2, pady=5)

        ttk.Button(self.main_frame, text="Reset Total Calories", command=self.reset_calories).grid(row=14, column=0, columnspan=2, pady=10)

        self.date_label = ttk.Label(self.main_frame, text=f"Date: {datetime.now().strftime('%d/%m/%Y')}")
        self.date_label.grid(row=15, column=0, columnspan=2, pady=5)

    def add_exercise(self):
        try:
            name = self.exercise_name.get().strip()
            duration_str = self.duration.get().strip()
            calories_str = self.calorie_burned.get().strip()
            
          
            if not name or not duration_str or not calories_str:
                messagebox.showerror("Error", "Please fill in all fields")
                return
                
            try:
                duration = float(duration_str)
                calories = float(calories_str)
            except ValueError:
                messagebox.showerror("Error", "Duration and calories must be numbers")
                return
                
            if duration <= 0 or calories <= 0:
                messagebox.showerror("Error", "Duration and calories must be positive numbers")
                return
                
       
            exercise = {
                "name": name,
                "duration": duration,
                "calories": calories,
                "date": self.current_date,
                "timestamp": datetime.now().strftime("%H:%M")
            }
            

            self.exercises.append(exercise)
            self.total_calories_burned += calories
            self.update_calories()
            self.update_history()
            self.save_data()

            self.exercise_name.delete(0, tk.END)
            self.duration.delete(0, tk.END)
            self.calorie_burned.delete(0, tk.END)
            
            messagebox.showinfo("Success", f"Exercise '{name}' added successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            print(f"Error adding exercise: {str(e)}")

    def add_calorie(self):
        try:
            name = self.food_name.get().strip()
            calories_str = self.calorie_intake.get().strip()
            
            if not name or not calories_str:
                messagebox.showerror("Error", "Please fill in all fields")
                return
                
            try:
                calories = float(calories_str)
            except ValueError:
                messagebox.showerror("Error", "Calories must be a number")
                return
                
            if calories <= 0:
                messagebox.showerror("Error", "Calories must be a positive number")
                return
                
         
            food = {
                "name": name,
                "calories": calories,
                "date": self.current_date,
                "timestamp": datetime.now().strftime("%H:%M")
            }
            

            self.food_intake.append(food)
            self.total_calories_intake += calories
            self.update_calories()
            self.update_history()
            self.save_data()

            self.food_name.delete(0, tk.END)
            self.calorie_intake.delete(0, tk.END)
            
            messagebox.showinfo("Success", f"Food '{name}' added successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            print(f"Error adding food: {str(e)}")

    def clear_entries(self):
        self.exercise_name.delete(0, tk.END)
        self.duration.delete(0, tk.END)
        self.calorie_burned.delete(0, tk.END)
        self.food_name.delete(0, tk.END)
        self.calorie_intake.delete(0, tk.END)

    def update_calories(self):

        self.total_calories_label.config(text=f"Total Calories Burned: {self.total_calories_burned:.1f}")
        self.total_intake_label.config(text=f"Total Calories Intake: {self.total_calories_intake:.1f}")
        

        net_calories = self.total_calories_intake - self.total_calories_burned
        self.net_calories_label.config(text=f"Net Calories: {net_calories:.1f}")

        progress = min(100, (self.total_calories_burned / self.target_calories) * 100)
        self.target_progress['value'] = progress
        self.target_label.config(text=f"Target Progress: {progress:.1f}%")
        
        
        if progress >= 100:
            self.target_progress.configure(style='Green.Horizontal.TProgressbar')
        elif progress >= 75:
            self.target_progress.configure(style='Yellow.Horizontal.TProgressbar')
        else:
            self.target_progress.configure(style='Red.Horizontal.TProgressbar')

    def save_data(self):
        data = {
            "exercises": self.exercises,
            "food_intake": self.food_intake,
            "total_calories_burned": self.total_calories_burned,
            "total_calories_intake": self.total_calories_intake,
            "history": self.history,
            "food_history": self.food_history,
            "current_date": self.current_date,
            "target_calories": self.target_calories,
            "activity_level": self.activity_level
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f)

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.exercises = data.get("exercises", [])
                    self.food_intake = data.get("food_intake", [])
                    self.total_calories_burned = data.get("total_calories_burned", 0)
                    self.total_calories_intake = data.get("total_calories_intake", 0)
                    self.history = data.get("history", [])
                    self.food_history = data.get("food_history", [])
                    self.current_date = data.get("current_date", datetime.now().strftime("%d/%m/%Y"))
                    self.target_calories = data.get("target_calories", 2000)
                    self.activity_level = data.get("activity_level", "Moderate")
                    
                  
                    for exercise in self.exercises:
                        if 'duration' not in exercise:
                            exercise['duration'] = 0
                    
                    self.update_calories()
                    self.update_history()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {str(e)}")
            print(f"Error loading data: {str(e)}")
            self.save_data()  

    def update_history(self):
    
        self.history_list.delete(0, tk.END)
        for exercise in reversed(self.exercises):
            entry = f"{exercise['timestamp']} - {exercise['name']}, {exercise.get('duration', 0)} min, {exercise['calories']} calories"
            self.history_list.insert(tk.END, entry)

      
        self.food_history_list.delete(0, tk.END)
        for food in reversed(self.food_intake):
            entry = f"{food['timestamp']} - {food['name']}, {food['calories']} calories"
            self.food_history_list.insert(tk.END, entry)

    def clear_history(self):
       
        self.exercises = []
        self.history_list.delete(0, tk.END)
        messagebox.showinfo("Success", "Exercise history cleared successfully!")
        self.save_data()
        self.update_history()

    def clear_food_history(self):
       
        self.food_intake = []
        self.food_history_list.delete(0, tk.END)
        messagebox.showinfo("Success", "Food history cleared successfully!")
        self.save_data()
        self.update_history()

    def reset_calories(self):
        """Reset all total calories, history, and progress"""
     
        self.total_calories_burned = 0
        self.total_calories_intake = 0
        
       
        self.exercises = []
        self.food_intake = []
        self.history_list.delete(0, tk.END)
        self.food_history_list.delete(0, tk.END)
        
        self.update_calories()
        self.update_history()
        self.save_data()
        messagebox.showinfo("Success", "All data has been reset successfully!")

    def export_data(self):
        """Export data to CSV"""
        try:
            filename = f"exercise_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w') as f:
                f.write("Type,Date,Time,Name,Duration,Calories\n")
                for item in self.exercises + self.food_intake:
                    item_type = "Exercise" if item in self.exercises else "Food"
                    duration = item.get('duration', '')
                    f.write(f"{item_type},{item['date']},{item['timestamp']}," 
                           f"{item['name']},{duration},{item['calories']}\n")
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {str(e)}")


    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = ttk.Label(self, text="BMI Calculator", font=('Arial', 16, 'bold'))
        label.pack(pady=10, padx=10)
        
        
        ttk.Label(self, text="Height (cm):").pack()
        self.height = ttk.Entry(self)
        self.height.pack()
        
        ttk.Label(self, text="Weight (kg):").pack()
        self.weight = ttk.Entry(self)
        self.weight.pack()
        
        self.result = ttk.Label(self, text="")
        self.result.pack(pady=10)
        
        ttk.Button(self, text="Calculate BMI", command=self.calculate_bmi).pack()
    
    def calculate_bmi(self):
        try:
            height = float(self.height.get()) / 100 
            weight = float(self.weight.get())
            bmi = weight / (height * height)
            category = self.get_bmi_category(bmi)
            self.result.config(text=f"BMI: {bmi:.1f} - {category}")
        except ValueError:
            self.result.config(text="Please enter valid numbers")
    
    def get_bmi_category(self, bmi):
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal weight"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"


    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = ttk.Label(self, text="Daily Calorie Needs Calculator", font=('Arial', 16, 'bold'))
        label.pack(pady=10, padx=10)
        
   
        ttk.Label(self, text="Age:").pack()
        self.age = ttk.Entry(self)
        self.age.pack()
        
        ttk.Label(self, text="Gender:").pack()
        self.gender = ttk.Combobox(self, values=["Male", "Female"])
        self.gender.pack()
        
        ttk.Label(self, text="Weight (kg):").pack()
        self.weight = ttk.Entry(self)
        self.weight.pack()
        
        ttk.Label(self, text="Height (cm):").pack()
        self.height = ttk.Entry(self)
        self.height.pack()
        
        ttk.Label(self, text="Activity Level:").pack()
        self.activity = ttk.Combobox(self, values=["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"])
        self.activity.pack()
        
        self.result = ttk.Label(self, text="")
        self.result.pack(pady=10)
        
        ttk.Button(self, text="Calculate Daily Calories", command=self.calculate_calories).pack()
    
    def calculate_calories(self):
        try:
            age = int(self.age.get())
            weight = float(self.weight.get())
            height = float(self.height.get())
            gender = self.gender.get()
            activity = self.activity.get()
            
          
            if gender == "Male":
                bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
            else:  
                bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
            
         
            activity_multiplier = {
                "Sedentary": 1.2,
                "Lightly Active": 1.375,
                "Moderately Active": 1.55,
                "Very Active": 1.725,
                "Extra Active": 1.9
            }.get(activity, 1.2)
            
            daily_calories = bmr * activity_multiplier
            self.result.config(text=f"Daily Calorie Needs: {daily_calories:.0f} calories")
        except ValueError:
            self.result.config(text="Please fill in all fields correctly")
