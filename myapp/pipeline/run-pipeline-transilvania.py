import subprocess
import os
import datetime

def run_step(script):
    print(f"Running {script}...")
    subprocess.run(["python", script], check=True)

def cleanup_intermediate_files():
    intermediate_files = [
        "step-1.txt",
        "step-2.txt",
        "step-3.txt",
    ]
    for file in intermediate_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Deleted {file}")

def rename_output_file():
    output_file = "output.csv"
    if os.path.exists(output_file):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        new_name = f"output_{timestamp}.csv"
        os.rename(output_file, new_name)
        print(f"Renamed {output_file} to {new_name}")
    else:
        print(f"{output_file} not found. Pipeline might have failed.")

def main():
    try:
        run_step("step-1.py")
        run_step("step-2-separators.py")
        run_step("step-3-tags.py")
        run_step("step-4-json.py")
        run_step("step-5-convert-csv.py")
        run_step("step-6-gpt.py")
        run_step("step-7-gpt-csv.py")
    except subprocess.CalledProcessError as e:
        print(f"Error: Step {e.cmd} failed.")
        exit(1)
        
    cleanup_intermediate_files()
    rename_output_file()
    print("Pipeline completed successfully.")

if __name__ == "__main__":
    main()
