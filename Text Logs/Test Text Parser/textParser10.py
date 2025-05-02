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

    # Split messages using timestamps as delimiters
    message_blocks = re.split(r'\n\[(\d+/\d+/\d+ \d+:\d+ [AP]M)\]', content)[1:]
    messages = []

    for i in range(0, len(message_blocks), 2):
        timestamp_str = message_blocks[i].strip()
        message_block = message_blocks[i + 1].strip()

        # Extract username
        username_match = re.match(r'([^\n]+)\n', message_block)
        username = username_match.group(1).strip() if username_match else "Unknown"

        # Extract message content
        content_match = re.search(r'\n(.*?)(?=\n(?:\{|\[)|$)', message_block, re.DOTALL)
        message_content = content_match.group(1).strip() if content_match else ""

        # Extract attachments from `{Attachments}` and `{Embed}` sections
        attachments = []
        attachment_matches = re.findall(r'https:\/\/cdn\.discordapp\.com\/attachments\/[^\s]+', message_block)
        embed_matches = re.findall(r'https:\/\/tenor\.com\/view\/[^\s]+', message_block)
        attachments.extend(attachment_matches)
        attachments.extend(embed_matches)

        # Remove attachments, embeds, and reactions from content
        message_content = re.sub(r'\{Attachments\}.*?(?:\n\n|$)', '', message_content, flags=re.DOTALL).strip()
        message_content = re.sub(r'\{Embed\}.*?(?:\n\n|$)', '', message_content, flags=re.DOTALL).strip()
        message_content = re.sub(r'\{Reactions\}.*?(?:\n\n|$)', '', message_content, flags=re.DOTALL).strip()
        message_content = re.sub(r'https:\/\/.*?(\s|\n|$)', '', message_content).strip()

        # Extract reactions
        reactions_match = re.search(r'\{Reactions\}\n(.*?)(?:\n\n|$)', message_block, re.DOTALL)
        reactions = [reaction.strip() for reaction in reactions_match.group(1).split('\n')] if reactions_match else []

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
            'reactions': reactions,
            'attachments': attachments  # Now includes GIFs from `{Embed}`
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
    fields = ['timestamp', 'username', 'channel', 'content', 'reactions', 'attachments']

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for message in messages:
            message['reactions'] = '|'.join(message['reactions']) if message['reactions'] else ''
            message['attachments'] = '|'.join(message['attachments']) if message['attachments'] else ''
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
