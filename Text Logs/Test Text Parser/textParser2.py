import re
import json
import os
from datetime import datetime
import argparse

def parse_discord_data(file_path):
    """
    Parse Discord chat data from the exported format into structured data.
    
    Args:
        file_path: Path to the raw Discord data file
    
    Returns:
        A list of message dictionaries with metadata
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Extract header information
    header_match = re.search(r'==+\nGuild: (.*)\nChannel: (.*)\nTopic: (.*)\n==+', content)
    metadata = {
        'guild': header_match.group(1) if header_match else None,
        'channel': header_match.group(2).split(' / ')[-1] if header_match else None,
        'topic': header_match.group(3) if header_match else None
    }
    
    # Extract messages
    message_pattern = r'\[(\d+/\d+/\d+ \d+:\d+ [AP]M)\] ([^\n]+)\n(.*?)(?=\[\d+/\d+/\d+ \d+:\d+ [AP]M\]|\Z)'
    messages = []
    
    for match in re.finditer(message_pattern, content, re.DOTALL):
        timestamp_str, author, content = match.groups()
        
        # Parse timestamp
        try:
            timestamp = datetime.strptime(timestamp_str, '%m/%d/%Y %I:%M %p')
            formatted_timestamp = timestamp.isoformat()
        except ValueError:
            formatted_timestamp = timestamp_str
        
        # Extract attachments
        attachments = []
        attachment_matches = re.finditer(r'{Attachments}\s+(https://[^\n]+)', content, re.MULTILINE)
        for att_match in attachment_matches:
            attachments.append(att_match.group(1))
        
        # Extract embeds
        embeds = []
        embed_section = re.search(r'{Embed}\s+(.*?)(?=\[|\Z)', content, re.DOTALL)
        if embed_section:
            embed_content = embed_section.group(1).strip()
            embed_links = [line.strip() for line in embed_content.split('\n') if line.strip()]
            embeds = embed_links
        
        # Extract reactions
        reactions = []
        reaction_section = re.search(r'{Reactions}\s+(.*?)(?=\[|\Z)', content, re.DOTALL)
        if reaction_section:
            reactions = [r.strip() for r in reaction_section.group(1).split('\n') if r.strip()]
        
        # Clean content by removing attachment, embed, and reaction sections
        clean_content = re.sub(r'{Attachments}.*?(?=\n\n|\n\[|\Z)', '', content, flags=re.DOTALL)
        clean_content = re.sub(r'{Embed}.*?(?=\n\n|\n\[|\Z)', '', clean_content, flags=re.DOTALL)
        clean_content = re.sub(r'{Reactions}.*?(?=\n\n|\n\[|\Z)', '', clean_content, flags=re.DOTALL)
        
        # Remove blank lines and leading/trailing whitespace
        clean_content = '\n'.join([line for line in clean_content.split('\n') if line.strip()])
        clean_content = clean_content.strip()
        
        # Create message object formatted for Label Studio
        message = {
            'timestamp': formatted_timestamp,
            'author': author,
            'text': clean_content,  # Using "text" as the default textKey for Label Studio
            'metadata': {
                'attachments': attachments,
                'embeds': embeds,
                'reactions': reactions,
                'channel': metadata['channel'],
                'guild': metadata['guild']
            }
        }
        
        messages.append(message)
    
    return messages, metadata

def save_for_label_studio(messages, output_file):
    """
    Save the messages in a format compatible with Label Studio
    
    Args:
        messages: List of message dictionaries
        output_file: Path to the output file
    """
    # Label Studio expects an array of objects
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(messages, f, indent=2)
        
def save_to_jsonl(messages, output_file):
    """
    Save the messages to a JSONL file format (one JSON object per line)
    
    Args:
        messages: List of message dictionaries
        output_file: Path to the output file
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for message in messages:
            f.write(json.dumps(message) + '\n')

def main():
    parser = argparse.ArgumentParser(description='Parse Discord chat data for Label Studio')
    parser.add_argument('input_file', help='Path to the raw Discord data file')
    parser.add_argument('--output', '-o', help='Output file path', default='discord_data_processed.json')
    parser.add_argument('--format', '-f', choices=['json', 'jsonl'], default='json', 
                        help='Output format (default: json)')
    
    args = parser.parse_args()
    
    messages, metadata = parse_discord_data(args.input_file)
    print(f"Extracted {len(messages)} messages from Discord data")
    
    if args.format == 'jsonl':
        save_to_jsonl(messages, args.output)
    else:
        save_for_label_studio(messages, args.output)
    
    print(f"Saved processed data to {args.output}")

if __name__ == "__main__":
    main()
