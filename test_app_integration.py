"""
Test App Integration - Test the integration of the gesture logger with the app
This script simulates the app's gesture detection process
"""

import subprocess
import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

class AppIntegrationTest:
    """Test the integration of the gesture logger with the app"""
    
    def __init__(self, root):
        """Initialize the test"""
        self.root = root
        self.root.title("App Integration Test")
        self.root.geometry("800x600")
        
        # Set up the UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI elements"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="App Integration Test", 
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=10)
        
        # Instructions
        instructions_label = ttk.Label(
            main_frame,
            text="This page tests the integration of the gesture logger with the app.",
            font=("Arial", 12)
        )
        instructions_label.pack(pady=10)
        
        # Test options frame
        options_frame = ttk.LabelFrame(main_frame, text="Test Options")
        options_frame.pack(pady=10, fill=tk.X)
        
        # Test options
        self.test_option = tk.StringVar(value="working_logger")
        
        # Working logger option
        working_logger_radio = ttk.Radiobutton(
            options_frame,
            text="Test Working Gesture Logger",
            variable=self.test_option,
            value="working_logger"
        )
        working_logger_radio.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Simple logger option
        simple_logger_radio = ttk.Radiobutton(
            options_frame,
            text="Test Simple Gesture Logger",
            variable=self.test_option,
            value="simple_logger"
        )
        simple_logger_radio.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        # Minimal logger option
        minimal_logger_radio = ttk.Radiobutton(
            options_frame,
            text="Test Minimal Gesture Logger",
            variable=self.test_option,
            value="minimal_logger"
        )
        minimal_logger_radio.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        # Test button
        test_button = ttk.Button(
            main_frame,
            text="Run Test",
            command=self._run_test
        )
        test_button.pack(pady=20)
        
        # Results frame
        self.results_frame = ttk.LabelFrame(main_frame, text="Test Results")
        self.results_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Results text
        self.results_text = tk.Text(self.results_frame, wrap=tk.WORD, height=15)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _run_test(self):
        """Run the selected test"""
        test_option = self.test_option.get()
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"Running test: {test_option}\n\n")
        
        if test_option == "working_logger":
            self._test_working_logger()
        elif test_option == "simple_logger":
            self._test_simple_logger()
        elif test_option == "minimal_logger":
            self._test_minimal_logger()
    
    def _test_working_logger(self):
        """Test the working gesture logger"""
        self.results_text.insert(tk.END, "Testing working gesture logger...\n")
        
        # Check if the working gesture logger exists
        if not os.path.exists("working_gesture_logger.py"):
            self.results_text.insert(tk.END, "Error: working_gesture_logger.py not found.\n")
            return
        
        # Run the working gesture logger
        try:
            self.results_text.insert(tk.END, "Launching working gesture logger...\n")
            self.root.update()
            
            result = subprocess.run(
                [sys.executable, "working_gesture_logger.py"],
                capture_output=True,
                text=True
            )
            
            # Display the output
            self.results_text.insert(tk.END, f"Output:\n{result.stdout}\n\n")
            
            # Process the result as the app would
            self._process_result(result.stdout)
            
        except Exception as e:
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
    
    def _test_simple_logger(self):
        """Test the simple gesture logger"""
        self.results_text.insert(tk.END, "Testing simple gesture logger...\n")
        
        # Check if the simple gesture logger exists
        if not os.path.exists("simple_gesture_logger.py"):
            self.results_text.insert(tk.END, "Error: simple_gesture_logger.py not found.\n")
            return
        
        # Run the simple gesture logger
        try:
            self.results_text.insert(tk.END, "Launching simple gesture logger...\n")
            self.root.update()
            
            result = subprocess.run(
                [sys.executable, "simple_gesture_logger.py"],
                capture_output=True,
                text=True
            )
            
            # Display the output
            self.results_text.insert(tk.END, f"Output:\n{result.stdout}\n\n")
            
            # Process the result as the app would
            self._process_result(result.stdout)
            
        except Exception as e:
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
    
    def _test_minimal_logger(self):
        """Test the minimal gesture logger"""
        self.results_text.insert(tk.END, "Testing minimal gesture logger...\n")
        
        # Create a minimal version of the gesture logger
        minimal_logger = """
import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime

def main():
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askyesno(
        "Gesture Detection",
        "Would you like to log 200ml of water with a peace sign gesture?"
    )
    if result:
        # Create the result data
        result_data = {
            "success": True,
            "gesture": "peace_sign",
            "timestamp": datetime.now().isoformat(),
            "amount": 200
        }
        
        # Save the result to a file
        with open("gesture_result.json", "w") as f:
            json.dump(result_data, f)
        
        print("GESTURE_DETECTED:peace_sign")
        return True
    else:
        # Create the result data
        result_data = {
            "success": False,
            "gesture": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save the result to a file
        with open("gesture_result.json", "w") as f:
            json.dump(result_data, f)
        
        print("NO_GESTURE_DETECTED")
        return False

if __name__ == "__main__":
    main()
        """
        
        # Save the minimal logger
        with open("minimal_gesture_logger.py", "w") as f:
            f.write(minimal_logger)
        
        # Run the minimal logger
        try:
            self.results_text.insert(tk.END, "Launching minimal gesture logger...\n")
            self.root.update()
            
            result = subprocess.run(
                [sys.executable, "minimal_gesture_logger.py"],
                capture_output=True,
                text=True
            )
            
            # Display the output
            self.results_text.insert(tk.END, f"Output:\n{result.stdout}\n\n")
            
            # Process the result as the app would
            self._process_result(result.stdout)
            
        except Exception as e:
            self.results_text.insert(tk.END, f"Error: {str(e)}\n")
    
    def _process_result(self, stdout):
        """Process the result as the app would"""
        self.results_text.insert(tk.END, "Processing result as the app would...\n")
        
        # Check if a gesture was detected from stdout
        gesture_detected = False
        gesture = None
        
        if "GESTURE_DETECTED" in stdout:
            gesture_detected = True
            gesture_line = [line for line in stdout.split('\n') if "GESTURE_DETECTED" in line][0]
            gesture = gesture_line.split(':')[1].strip()
            self.results_text.insert(tk.END, f"Detected gesture from stdout: {gesture}\n")
        else:
            self.results_text.insert(tk.END, "No gesture detected from stdout.\n")
        
        # Check if the result file exists
        if os.path.exists("gesture_result.json"):
            try:
                with open("gesture_result.json", "r") as f:
                    result_data = json.load(f)
                
                self.results_text.insert(tk.END, f"Result file content:\n{json.dumps(result_data, indent=2)}\n\n")
                
                if result_data.get('success', False):
                    self.results_text.insert(tk.END, f"Success: {result_data.get('success')}\n")
                    self.results_text.insert(tk.END, f"Gesture: {result_data.get('gesture')}\n")
                    self.results_text.insert(tk.END, f"Amount: {result_data.get('amount')} ml\n")
                    
                    # This is what the app would return
                    app_result = {
                        'success': True,
                        'gesture': result_data.get('gesture'),
                        'confidence': 0.9,
                        'amount': result_data.get('amount', 200),
                        'annotated_image': None
                    }
                    
                    self.results_text.insert(tk.END, f"\nApp would return:\n{json.dumps(app_result, indent=2)}\n")
                    self.results_text.insert(tk.END, "\nTEST PASSED: Gesture detected and processed correctly.\n")
                else:
                    self.results_text.insert(tk.END, "Result file indicates no gesture was detected.\n")
                    
                    # This is what the app would return
                    app_result = {
                        'success': False,
                        'error': "No gesture detected",
                        'gesture': None,
                        'annotated_image': None
                    }
                    
                    self.results_text.insert(tk.END, f"\nApp would return:\n{json.dumps(app_result, indent=2)}\n")
                    self.results_text.insert(tk.END, "\nTEST PASSED: No gesture detected, handled correctly.\n")
            except Exception as e:
                self.results_text.insert(tk.END, f"Error reading result file: {str(e)}\n")
                self.results_text.insert(tk.END, "\nTEST FAILED: Error processing result file.\n")
        else:
            self.results_text.insert(tk.END, "No result file found.\n")
            self.results_text.insert(tk.END, "\nTEST FAILED: No result file created.\n")

def main():
    """Main function"""
    root = tk.Tk()
    app = AppIntegrationTest(root)
    root.mainloop()

if __name__ == "__main__":
    main()
