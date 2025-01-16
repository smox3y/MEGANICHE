import subprocess
import time
import random

# Define the script to run (automized version of MEGANICHE.py)
script_to_run = "MEGANICHE.py"

# Time to run the script in seconds (30 minutes)
RUN_TIME = 30 * 60

# Main function to run the script with a timer
def main():
    print(f"Starting the automated timer for {script_to_run}...\n")

    while True:  # Infinite loop to keep running the script
        try:
            print(f"\nStarting script: {script_to_run}")
            start_time = time.time()

            # Start the script as a subprocess
            process = subprocess.Popen(["python", script_to_run])

            # Keep the script running for the allocated time
            while time.time() - start_time < RUN_TIME:
                time.sleep(10)  # Check every 10 seconds if time has passed
                if process.poll() is not None:  # If script finishes early
                    print(f"{script_to_run} has exited before 30 minutes.")
                    break

            # Terminate the script after 30 minutes if still running
            if process.poll() is None:
                process.terminate()
                print(f"{script_to_run} has been stopped after 30 minutes.")

        except Exception as e:
            print(f"Error running {script_to_run}: {e}")

        # Pause for 10 seconds before running the script again
        time.sleep(10)

if __name__ == "__main__":
    main()
