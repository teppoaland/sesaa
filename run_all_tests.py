import subprocess
import sys

test_files = [
    "Total_Installation_From_GP_automation.py",
    "Total_Activation_automation.py",
    "Total_Enable_features_automation.py"
]

print("🚀 Starting all tests...\n")

for test_file in test_files:
    print(f"📋 Running {test_file}...")
    try:
        result = subprocess.run([sys.executable, test_file], check=True)
        print(f"✅ {test_file} passed!\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ {test_file} failed with error: {e}")
        sys.exit(1)

print("🎉 All tests completed successfully!")