import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import json
import os
import math
from typing import List, Dict, Optional
import webbrowser
import requests
from PIL import Image, ImageTk
import threading
import time

class ExerciseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Daily Exercise and Calorie Tracker")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        

        self.data_file = "exercise_data.json"
        self.exercises: List[Dict] = []
        self.food_intake: List[Dict] = []
        self.total_calories_burned: float = 0
        self.total_calories_intake: float = 0
        self.history: List[Dict] = []
        self.current_date: str = datetime.now().strftime("%d/%m/%Y")
        

        self.target_calories: float = 2000  # Default daily target
        self.activity_level: str = "Moderate"
        
  
        self.create_widgets()
        self.load_data()
        self.update_calories()
        self.update_history()
        
       
        self.auto_save_timer = None
        self.start_auto_save()

    def create_widgets(self):

        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

   
        self.history_frame = ttk.Frame(self.root, padding="10")
        self.history_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

  
        ttk.Label(self.history_frame, text="Exercise History", font=('Arial', 14, 'bold')).pack(pady=10)
        
  
        self.history_list = tk.Listbox(self.history_frame, width=50, height=25)
        self.history_list.pack(fill=tk.BOTH, expand=True)
        
  
        ttk.Button(self.history_frame, text="Clear History", command=self.clear_history).pack(pady=10)

   
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

    
        ttk.Label(self.main_frame, text="Add Food", font=('Arial', 14, 'bold')).grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Label(self.main_frame, text="Food Name:").grid(row=6, column=0, sticky=tk.W)
        self.food_name = ttk.Entry(self.main_frame)
        self.food_name.grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(self.main_frame, text="Calories:").grid(row=7, column=0, sticky=tk.W)
        self.calorie_intake = ttk.Entry(self.main_frame)
        self.calorie_intake.grid(row=7, column=1, padx=5, pady=5)

        ttk.Button(self.main_frame, text="Add Food", command=self.add_calorie).grid(row=8, column=0, columnspan=2, pady=10)

      
        ttk.Label(self.main_frame, text="Total Calories", font=('Arial', 14, 'bold')).grid(row=9, column=0, columnspan=2, pady=10)
        
        self.total_calories_label = ttk.Label(self.main_frame, text="Total Calories Burned: 0")
        self.total_calories_label.grid(row=10, column=0, columnspan=2, pady=5)
        
        self.total_intake_label = ttk.Label(self.main_frame, text="Total Calories Intake: 0")
        self.total_intake_label.grid(row=11, column=0, columnspan=2, pady=5)
        
        self.net_calories_label = ttk.Label(self.main_frame, text="Net Calories: 0")
        self.net_calories_label.grid(row=12, column=0, columnspan=2, pady=5)
        
        self.target_progress = ttk.Progressbar(self.main_frame, orient='horizontal', length=200, mode='determinate')
        self.target_progress.grid(row=13, column=0, columnspan=2, pady=5)
        
        self.target_label = ttk.Label(self.main_frame, text="Target Progress: 0%")
        self.target_label.grid(row=14, column=0, columnspan=2, pady=5)

     
        self.date_label = ttk.Label(self.main_frame, text=f"Date: {datetime.now().strftime('%d/%m/%Y')}")
        self.date_label.grid(row=15, column=0, columnspan=2, pady=5)

    def add_exercise(self):
        try:
            name = self.exercise_name.get().strip()
            duration_str = self.duration.get().strip()
            calories_str = self.calorie_burned.get().strip()
            
            # Validate input
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
            "target_calories": self.target_calories,
            "activity_level": self.activity_level,
            "current_date": self.current_date
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f)

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.exercises = data.get('exercises', [])
                    self.food_intake = data.get('food_intake', [])
                    self.total_calories_burned = data.get('total_calories_burned', 0)
                    self.total_calories_intake = data.get('total_calories_intake', 0)
                    self.history = data.get('history', [])
                    self.target_calories = data.get('target_calories', 2000)
                    self.activity_level = data.get('activity_level', 'Moderate')
                    self.current_date = data.get('current_date', datetime.now().strftime("%d/%m/%Y"))
                    self.update_calories()
                    self.update_history()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {str(e)}")
            print(f"Error loading data: {str(e)}")

    def update_history(self):
        self.history_list.delete(0, tk.END)
        for item in reversed(self.history):
            self.history_list.insert(tk.END, item)

    def clear_history(self):
        self.history = []
        self.history_list.delete(0, tk.END)
        messagebox.showinfo("Başarılı", "Geçmiş başarıyla temizlendi!")
        self.save_data()

    def start_auto_save(self):
        """Start auto-save timer"""
        self.auto_save_timer = threading.Timer(300, self.auto_save)
        self.auto_save_timer.daemon = True
        self.auto_save_timer.start()

    def auto_save(self):
        """Auto-save data every 5 minutes"""
        try:
            self.save_data()
            print("Auto-save completed successfully")
        except Exception as e:
            print(f"Error during auto-save: {str(e)}")
        finally:
            self.start_auto_save()

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

    def show_stats(self):
        """Show detailed statistics"""
        try:
            stats = {
                'Total Exercises': len(self.exercises),
                'Total Foods': len(self.food_intake),
                'Average Exercise Duration': sum(e['duration'] for e in self.exercises) / len(self.exercises) if self.exercises else 0,
                'Average Calories Burned': sum(e['calories'] for e in self.exercises) / len(self.exercises) if self.exercises else 0,
                'Average Calories Intake': sum(f['calories'] for f in self.food_intake) / len(self.food_intake) if self.food_intake else 0
            }
            
            stats_text = "Detailed Statistics:\n\n"
            for key, value in stats.items():
                stats_text += f"{key}: {value:.1f}\n"
            
            messagebox.showinfo("Statistics", stats_text)
        except Exception as e:
            messagebox.showerror("Error", f"Error showing statistics: {str(e)}")

    def change_date(self):
        """Change current date"""
        try:
            from tkinter import simpledialog
            new_date = simpledialog.askstring("Change Date", "Enter new date (DD/MM/YYYY):", 
                                            initialvalue=self.current_date)
            if new_date:
                try:
                    datetime.strptime(new_date, "%d/%m/%Y")
                    self.current_date = new_date
                    self.date_label.config(text=f"Date: {self.current_date}")
                    self.save_data()
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format. Please use DD/MM/YYYY")
        except Exception as e:
            messagebox.showerror("Error", f"Error changing date: {str(e)}")

    def get_exercise_recommendations(self):
        """Get exercise recommendations based on activity level"""
        try:
            recommendations = {
                'Low': "Walking, Yoga, Light stretching",
                'Moderate': "Jogging, Cycling, Swimming, HIIT",
                'High': "Running, Weightlifting, CrossFit, Boxing"
            }
            
            messagebox.showinfo("Exercise Recommendations", 
                              f"Based on your activity level ({self.activity_level}):\n\n" + 
                              recommendations.get(self.activity_level, "No recommendations available"))
        except Exception as e:
            messagebox.showerror("Error", f"Error getting recommendations: {str(e)}")

    def open_nutrition_calculator(self):
        """Open nutrition calculator in web browser"""
        try:
            webbrowser.open("https://www.calculator.net/calorie-calculator.html")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening nutrition calculator: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExerciseTracker(root)
    root.mainloop()