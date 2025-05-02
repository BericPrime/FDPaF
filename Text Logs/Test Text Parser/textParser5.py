import re
import csv
import datetime
from typing import List, Dict, Any

def parse_discord_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse Discord data from a text file into a structured format.
    
    Args:
        file_path: Path to the Discord data text file
        
    Returns:
        List of dictionaries containing message data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract channel information
    channel_match = re.search(r'Channel: (.*?)\nTopic:', content)
    channel = channel_match.group(1).strip() if channel_match else "Unknown"
    
    # Split messages
    message_blocks = re.split(r'\n\[', content)
    
    # Skip the header
    message_blocks = [block for block in message_blocks if re.search(r'\d+/\d+/\d+ \d+:\d+ [AP]M\]', block)]
    
    messages = []
    
    for i, block in enumerate(message_blocks):
        if i == 0:
            # Handle the first block which doesn't start with '['
            block = '[' + block
        else:
            # Add back the '[' that was removed during splitting
            block = '[' + block
        
        # Extract timestamp and username
        timestamp_user_match = re.match(r'\[(\d+/\d+/\d+ \d+:\d+ [AP]M)\] ([^\n]+)', block)
        
        if timestamp_user_match:
            timestamp_str = timestamp_user_match.group(1)
            username = timestamp_user_match.group(2).strip()
            
            # Extract message content
            content_match = re.search(r'\[(\d+/\d+/\d+ \d+:\d+ [AP]M)\] ([^\n]+)\n\n(.*)', block, re.DOTALL)
            
            message_content = ''
            if content_match:
                message_content = content_match.group(3).strip()
            
            # Check for and handle attachments
            attachment_match = re.search(r'\{Attachments\}\n(.*?)(?:\n\n|$)', message_content, re.DOTALL)
            attachments = []
            if attachment_match:
                attachments = [url.strip() for url in attachment_match.group(1).split('\n') if url.strip()]
                # Remove the attachments section from message content
                message_content = re.sub(r'\{Attachments\}\n.*?(?:\n\n|$)', '', message_content, flags=re.DOTALL)
            
            # Check for and handle embeds
            embed_match = re.search(r'\{Embed\}\n(.*?)(?:\n\n|$)', message_content, re.DOTALL)
            embeds = []
            if embed_match:
                embeds = [url.strip() for url in embed_match.group(1).split('\n') if url.strip()]
                # Remove the embeds section from message content
                message_content = re.sub(r'\{Embed\}\n.*?(?:\n\n|$)', '', message_content, flags=re.DOTALL)
            
            # Check for and handle reactions
            reactions_match = re.search(r'\{Reactions\}\n(.*?)(?:\n\n|$)', message_content, re.DOTALL)
            reactions = []
            if reactions_match:
                reactions = [reaction.strip() for reaction in reactions_match.group(1).split('\n') if reaction.strip()]
                # Remove the reactions section from message content
                message_content = re.sub(r'\{Reactions\}\n.*?(?:\n\n|$)', '', message_content, flags=re.DOTALL)
            
            # Clean up the message content
            message_content = message_content.strip()
            
            # Convert timestamp to ISO format
            try:
                dt = datetime.datetime.strptime(timestamp_str, '%m/%d/%Y %I:%M %p')
                iso_timestamp = dt.isoformat()
            except ValueError:
                iso_timestamp = timestamp_str
            
            message_data = {
                'timestamp': iso_timestamp,
                'username': username,
                'channel': channel,
                'content': message_content,
                'attachments': attachments,
                'embeds': embeds,
                'reactions': reactions
            }
            
            messages.append(message_data)
    
    return messages

def save_to_csv(messages: List[Dict[str, Any]], output_path: str) -> None:
    """
    Save parsed messages to a CSV file.
    
    Args:
        messages: List of message dictionaries
        output_path: Path to save the CSV file
    """
    # Define CSV fields
    fields = ['timestamp', 'username', 'channel', 'content', 'attachments', 'embeds', 'reactions']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        
        for message in messages:
            # Convert lists to strings for CSV format
            message['attachments'] = '|'.join(message['attachments'])
            message['embeds'] = '|'.join(message['embeds'])
            message['reactions'] = '|'.join(message['reactions'])
            
            writer.writerow(message)

def main():
    input_file = "data.txt"  # Update this path if needed
    output_file = "discord_data.csv"
    
    print(f"Parsing Discord data from {input_file}...")
    messages = parse_discord_data(input_file)
    
    print(f"Saving {len(messages)} messages to {output_file}...")
    save_to_csv(messages, output_file)
    
    print("Done!")

if __name__ == "__main__":
    main()
