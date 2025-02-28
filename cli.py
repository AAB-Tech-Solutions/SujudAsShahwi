import argparse
from sujud_as_shahwi import SujudAsShahwi

def main():
    parser = argparse.ArgumentParser(description="Sujud As-Shahwi CLI")
    parser.add_argument("command", choices=["search", "view"], help="Command to execute")
    parser.add_argument("input", nargs="?", help="Input text for the search command")

    args = parser.parse_args()
    sujud = SujudAsShahwi()

    if args.command == "search":
        if not args.input:
            print("Please provide input text for the search command.")
        else:
            result = sujud.search_mistake(args.input)
            print(result)
    elif args.command == "view":
        rules = sujud.view_all_rules()
        for mistake, correction in rules.items():
            print(f"Mistake: {mistake}\nCorrection: {correction}\n")

if __name__ == "__main__":
    main()
