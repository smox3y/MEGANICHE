#TTMEGA.py
import subprocess
import time
import random
from datetime import datetime

# Define the script to run (automized version of MEGANICHE.py)
script_to_run = "MEGANICHE.py"

# Initial run time in seconds (30 minutes)
RUN_TIME = 30 * 60

# Initial pause time in seconds (10 seconds)
pause_time = 10

# Main function to run the script with a timer
def main():
    print(f"Starting the automated timer for {script_to_run}...\n")

    while True:  # Infinite loop to keep running the script
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{current_time}] Starting script: {script_to_run}")
            start_time = time.time()

            # Start the script as a subprocess
            process = subprocess.Popen(["python", script_to_run])

            # Keep the script running for the allocated time
            while time.time() - start_time < RUN_TIME:
                time.sleep(10)  # Check every 10 seconds if time has passed
                if process.poll() is not None:  # If script finishes early
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {script_to_run} has exited before {RUN_TIME / 60} minutes.")
                    break

            # Terminate the script after the allocated run time if still running
            if process.poll() is None:
                process.terminate()
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {script_to_run} has been stopped after {RUN_TIME / 60} minutes.")

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error running {script_to_run}: {e}")

        # Pause before the next run, incrementing the pause time by 10%
        global pause_time
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Pausing for {pause_time} seconds before the next run...")
        time.sleep(pause_time)
        pause_time *= 1.1  # Increment pause time by 10%

if __name__ == "__main__":
    main()
