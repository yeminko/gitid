import time

for i in range(1, 6):
    # \r resets the cursor to the beginning of the line each loop
    print(f"\rProgress: {i}/5", end="", flush=True)
    time.sleep(1)

print("\nFinished!")  # Add \n at the end so future prints go to the next line
