import praw
import sys
import io
import traceback
import json
from datetime import datetime

# On Windows, fix console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Set up Reddit instance
reddit = praw.Reddit(
    client_id='EoLQtxyuMb20bIlSUGn5MQ',
    client_secret='9UemwiJ8qPRdt_xFlf-dy4gW_KGROA',
    user_agent='strategy_scraper by /u/Complex_Meringue2368'
)

# Generate timestamp for filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f"clash_royale_mistral_training_{timestamp}.jsonl"

subreddit = reddit.subreddit("ClashRoyale")
limit = 1000  # Total posts to process

# Define the flairs you want to search for
target_flairs = ["Strategy", "Discussion", "Deck"]

print(f"Starting search for posts with {target_flairs} flairs in r/ClashRoyale...")
print(f"Results will be saved to {output_file}")

# Process comments recursively and add them to the messages list
def process_comments(comment, messages, indent_level=0):
    if comment.body == "[deleted]" or not comment.author:
        return
    
    # Add comment to messages
    author_name = comment.author.name if comment.author else "Unknown"
    
    messages.append({
        "role": "user" if indent_level % 2 == 0 else "assistant",
        "content": comment.body
    })
    
    # Process replies in order
    for reply in comment.replies:
        process_comments(reply, messages, indent_level + 1)

# Open file for writing
with open(output_file, 'w', encoding='utf-8') as out_file:
    # Get new posts
    hot = subreddit.new(limit=None)

    # Process posts
    n = 0
    for post in hot:
        if post.link_flair_text in target_flairs:
            n += 1
            print(f"Processing post #{n}: '{post.title}'")
            
            try:
                # Skip posts by deleted authors or with empty text
                if not post.author or not post.selftext or post.selftext == "[deleted]":
                    continue
                
                # Start a new conversation for each post
                messages = []
                
                # Add the post as the first message (system prompt)
                messages.append({
                    "role": "system", 
                    "content": f"Title: {post.title}\n\n{post.selftext}"
                })
                
                # Load all comments
                post.comments.replace_more(limit=None)
                
                # Process all top-level comments and their replies
                for top_comment in post.comments:
                    process_comments(top_comment, messages)
                
                # Skip posts with too few messages
                if len(messages) < 3:  # At least system + 2 conversation turns
                    continue
                    
                # Write the conversation to the JSONL file
                conversation = {
                    "messages": messages,
                    "metadata": {
                        "post_id": post.id,
                        "flair": post.link_flair_text,
                        "timestamp": post.created_utc
                    }
                }
                
                out_file.write(json.dumps(conversation) + "\n")
                out_file.flush()  # Save progress
                
            except Exception as e:
                print(f"Error processing post {post.id}: {str(e)}")
                traceback.print_exc()
            
            # Check if we've processed enough posts
            if n >= limit:
                break
                
    print(f"\nProcessed {n} posts with the specified flairs.")
    print(f"Results saved to {output_file}")