# run_robot_tests.py
import subprocess
import sys
import os

def run_robot_tests():
    # Luo output-kansio raporteille
    output_dir = "robot-reports"
    os.makedirs(output_dir, exist_ok=True)
    
    # Aja Robot Framework -testit
    result = subprocess.run([
        "robot", 
        "--outputdir", output_dir,
        "--log", "robot-log.html",
        "--report", "robot-report.html",
        "--xunit", "robot-xunit.xml",
        "weather_app_tests.robot"
    ], capture_output=True, text=True)
    
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_robot_tests())