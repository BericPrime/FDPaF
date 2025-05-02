import csv

# Function to parse chat data and extract structured information
def parse_chat_data(file_path):
    data = []  # List to store parsed chat entries
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            
            # Skip empty lines or metadata lines
            if not line or line.startswith("="):
                continue
            
            # Extract timestamp, user, and message
            try:
                timestamp = line.split("]")[0].strip("[")
                user_message = line.split("]")[1].split(": ", 1)
                user = user_message[0].strip()
                message = user_message[1].strip() if len(user_message) > 1 else "No message"
                data.append({"Timestamp": timestamp, "User": user, "Message": message})
            except IndexError:
                # Handle lines that don't conform to the expected format
                print(f"Skipping line due to unexpected format: {line}")
    
    return data

# Function to write data to CSV
def write_to_csv(data, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Timestamp', 'User', 'Message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Main execution
if __name__ == "__main__":
    input_file = "data.txt"  # Replace with your input file path
    output_file = "parsed_chat_data.csv"
    
    parsed_data = parse_chat_data(input_file)
    write_to_csv(parsed_data, output_file)
    
    print(f"Chat data has been successfully written to {output_file}!")
