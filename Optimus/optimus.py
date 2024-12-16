import subprocess
import time
import os
import random

# Define the scripts to run
scripts = [
    "megaIG.py",      # Instagram Script
    "MEGANICHE.py",   # TikTok Script 1
    "megaIGDM.py",      # Instagram Script
    "ytoutreach.py"   # YouTube Reels Script
]

# Time to run each script in seconds (30 minutes)
RUN_TIME = 30 * 60

# Main function to run scripts randomly
def main():
    print("Starting the script manager...\n")
    
    while True:  # Infinite loop to keep running the scripts
        script = random.choice(scripts)  # Pick a random script
        try:
            print(f"\nStarting script: {script}")
            start_time = time.time()

            # Start the script as a subprocess
            process = subprocess.Popen(["python", script])
            
            # Keep the script running for the allocated time
            while time.time() - start_time < RUN_TIME:
                time.sleep(10)  # Check every 10 seconds if time has passed
                if process.poll() is not None:  # If script finishes early
                    print(f"{script} has exited before 30 minutes.")
                    break
            
            # Terminate the script after 30 minutes if still running
            process.terminate()
            print(f"{script} has been stopped after 30 minutes.")

        except Exception as e:
            print(f"Error running {script}: {e}")

        time.sleep(10)  # Pause for 10 seconds before running the next script

if __name__ == "__main__":
    main()
