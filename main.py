import sys
import logging
import time
from sujud_as_shahwi import SujudAsShahwi
from config import configure_logging
from timer import Timer  # Import the Timer class

# Configure logging
success_logger, error_logger = configure_logging()

def main():
    success_logger.info("Program started")
    sujud_as_shahwi = SujudAsShahwi()
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <prayer mistake description>")
        return
    
    user_input = " ".join(sys.argv[1:])
    success_logger.info(f"User input: {user_input}")
    try:
        timer = Timer()  # Start the timer
        print("Timer started.")
        
        while True:
            command = input("Enter command (stop, reset, pause, resume, elapsed, remaining, exit): ").strip().lower()
            
            if command == "stop":
                elapsed = timer.stop()
                print(f"Timer stopped. Elapsed time: {elapsed:.2f} seconds")
            elif command == "reset":
                timer.reset()
                print("Timer reset.")
            elif command == "pause":
                timer.pause()
                print("Timer paused.")
            elif command == "resume":
                timer.resume()
                print("Timer resumed.")
            elif command == "elapsed":
                elapsed = timer.get_elapsed_time()
                print(f"Elapsed time: {elapsed:.2f} seconds")
            elif command == "remaining":
                duration = float(input("Enter duration in seconds: "))
                remaining = timer.get_remaining_time(duration)
                print(f"Remaining time: {remaining:.2f} seconds")
            elif command == "exit":
                print("Exiting.")
                break
            else:
                print("Unknown command.")
        
        result = sujud_as_shahwi.search_mistake(user_input)
        time_taken = timer.stop()  # Stop the timer and get the elapsed time
        success_logger.info(f"Time taken for search: {time_taken:.2f} seconds")
        if result:
            print(result)
            success_logger.info(f"Successful search for: {user_input}")
            success_logger.info(f"Result: {result}")
        else:
            print("No matching mistake found.")
            success_logger.info(f"No matching mistake found for: {user_input}")
    except Exception as e:
        error_logger.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
    finally:
        success_logger.info("Program ended")

if __name__ == "__main__":
    main()
