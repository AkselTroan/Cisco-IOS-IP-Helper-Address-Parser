from file_handlers.pan import interpretAndSave
from ios_generation.gen import generateNewConfig
import time


def main():

    # Start timer
    start = time.perf_counter()

    interpretAndSave()


    # Next To Do: Analyze the file and generate config
    generateNewConfig()
    
    # Stop timer
    stop = time.perf_counter()

    print(f"Total runtime: {stop - start:0.4f} seconds")

if __name__ == "__main__":
    main()
