import os
import json
import openai
from dotenv import load_dotenv
import creds
load_dotenv()  # This will load variables from .env
openai.api_key = os.getenv("OPENAI_API_KEY")

# ------------------------- Data Store -------------------------
destinations = []

# ------------------------- Destination Functions -------------------------
def add_destination(city, country, start_date, end_date, budget, activities):
    destination = {
        "city": city,
        "country": country,
        "start_date": start_date,
        "end_date": end_date,
        "budget": budget,
        "activities": [act.strip() for act in activities.split(",")]
    }
    destinations.append(destination)
    print(f"\n Destination '{city}, {country},{start_date},{end_date},{budget},{activities}' added successfully.")

def view_destination():
    if not destinations:
        print("\n No destinations found.")
        return
    print("\n Saved Destinations:")
    for dest in destinations:
        print(f"- {dest['city']}, {dest['country']} from {dest['start_date']} to {dest['end_date']} | Budget: {dest['budget']} | Activities: {', '.join(dest['activities'])}")

def update_destination(city, country, start_date, end_date, budget, activities):
    for dest in destinations:
        if dest["city"].lower() == city.lower():
            dest["country"] = country
            dest["start_date"] = start_date
            dest["end_date"] = end_date
            dest["budget"] = budget
            dest["activities"] = [act.strip() for act in activities.split(",")]
            print(f"\n Destination '{city}' updated successfully!")
            return
    print(" Destination not found!")

def remove_destination(city):
    global destinations
    before = len(destinations)
    destinations = [dest for dest in destinations if dest["city"].lower() != city.lower()]
    after = len(destinations)
    if before == after:
        print(" No matching destination found.")
    else:
        print(f" Destination '{city}' removed successfully.")

def search_destination(destinations, query):
    query = query.lower()
    results = []
    for dest in destinations:
        if (query in dest["city"].lower() or
            query in dest["country"].lower() or
            any(query in activity.lower() for activity in dest["activities"])):
            results.append(dest)
    return results

# ------------------------- Save & Load Destinations -------------------------
def save_destinations_to_file(filename="destinations.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(destinations, f, indent=4)
    print(" All destinations saved successfully.")

def load_destinations_from_file(filename="destinations.json"):
    global destinations
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            destinations = json.load(f)
        print(" Destinations loaded successfully.")
    else:
        print(" No saved destination file found.")

# ------------------------- AI Itinerary Generator -------------------------
def generate_itinerary():
    print("\n Generate a Daily Travel Itinerary")

    destination = input("Enter your destination: ").strip()
    if not destination:
        print(" Destination cannot be empty.")
        return

    try:
        days = int(input("How many days are you staying? ").strip())
        if days <= 0:
            print(" Number of days must be at least 1.")
            return
    except ValueError:
        print(" Please enter a valid number for days.")
        return

    interests = input("What are your interests? (e.g., history, food, adventure): ").strip()

    prompt = (
        f"Create a {days}-day travel itinerary for {destination}. "
        f"The traveler is interested in {interests or 'general attractions'}. "
        f"Each day should include a morning, afternoon, and evening plan. "
        f"Be detailed but concise."
    )

    try:

        if not creds.api_key:
            print(" OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            return

        openai.api_key = creds.api_key

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional travel planner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        itinerary_text = response.choices[0].message["content"]
        print("\n Your AI-Powered Travel Itinerary:\n")
        print(itinerary_text)

        save = input("\nWould you like to save this itinerary? (yes/no): ").lower()
        if save in ["yes", "y"]:
            fmt = input("Save as 'txt' or 'json'? ").lower()
            save_itinerary_to_file(itinerary_text, destination, fmt)

    except Exception as e:
        print(f" An error occurred: {e}")

# ------------------------- Save AI Itinerary -------------------------
def save_itinerary_to_file(itinerary_text, destination, file_format="txt"):
    folder = "itineraries"
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = f"{destination.lower().replace(' ', '_')}_itinerary.{file_format}"
    path = os.path.join(folder, filename)

    try:
        if file_format == "txt":
            with open(path, "w", encoding="utf-8") as file:
                file.write(itinerary_text)
        elif file_format == "json":
            itinerary_data = {
                "destination": destination,
                "itinerary": itinerary_text
            }
            with open(path, "w", encoding="utf-8") as file:
                json.dump(itinerary_data, file, indent=4)
        else:
            print(" Unsupported format.")
            return

        print(f" Itinerary saved as '{filename}'.")

    except Exception as e:
        print(f" Error saving the file: {e}")

# ------------------------- Load AI Itinerary -------------------------
def load_itinerary():
    folder = "itineraries"
    if not os.path.exists(folder):
        print(" No saved itineraries folder found.")
        return

    files = [f for f in os.listdir(folder) if f.endswith(".json")]
    if not files:
        print(" No itinerary files found.")
        return

    print("\n Saved Itineraries:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")

    try:
        choice = int(input("Enter the number of the itinerary to load: "))
        if 1 <= choice <= len(files):
            path = os.path.join(folder, files[choice - 1])
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"\n Loaded Itinerary for {data['destination']}:\n")
            print(data["itinerary"])
        else:
            print(" Invalid selection.")
    except Exception as e:
        print(f" Error loading file: {e}")

# ------------------------- Exit Program -------------------------
def exit_program():
    save_destinations_to_file()
    print("\n Thank you for using the AI Travel Itinerary Planner. Safe travels!")
    exit()

# ------------------------- Main Menu -------------------------
def main_menu():
    load_destinations_from_file()

    while True:
        print("\n Travel Itinerary Planner Menu:")
        print("1. Add Destination")
        print("2. Remove Destination")
        print("3. Update Destination")
        print("4. View All Destinations")
        print("5. Search Destination")
        print("6. AI Travel Assistance (Generate Itinerary)")
        print("7. Save All Destinations")
        print("8. Load Saved AI Itinerary")
        print("9. Exit")

        choice = input("Enter your choice (1-9): ")

        if choice == "1":
            city = input("City: ")
            country = input("Country: ")
            start = input("Start Date (YYYY-MM-DD): ")
            end = input("End Date (YYYY-MM-DD): ")
            budget = input("Budget: ")
            activities = input("Activities (comma-separated): ")
            add_destination(city, country, start, end, budget, activities)

        elif choice == "2":
            city = input("Enter city to remove: ")
            remove_destination(city)

        elif choice == "3":
            city = input("City to update: ")
            country = input("New Country: ")
            start = input("New Start Date: ")
            end = input("New End Date: ")
            budget = input("New Budget: ")
            activities = input("New Activities (comma-separated): ")
            update_destination(city, country, start, end, budget, activities)

        elif choice == "4":
            view_destination()

        elif choice == "5":
            query = input("Enter a city, country, or activity to search: ")
            results = search_destination(destinations, query)
            if results:
                print("\n Search Results:")
                for dest in results:
                    print(f"{dest['city']}, {dest['country']} | Activities: {', '.join(dest['activities'])}")
            else:
                print(" No matching results.")

        elif choice == "6":
            generate_itinerary()

        elif choice == "7":
            save_destinations_to_file()

        elif choice == "8":
            load_itinerary()

        elif choice == "9":
            exit_program()

        else:
            print(" Invalid choice. Please select 1-9.")

# ------------------------- Start App -------------------------
main_menu()
