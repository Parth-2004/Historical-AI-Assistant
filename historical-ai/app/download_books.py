import requests
import os

# Project Gutenberg IDs for 19th Century Classics
BOOKS = {
    "Frankenstein (Mary Shelley)": "https://www.gutenberg.org/cache/epub/84/pg84.txt",
    "Pride and Prejudice (Jane Austen)": "https://www.gutenberg.org/cache/epub/1342/pg1342.txt",
    "A Tale of Two Cities (Charles Dickens)": "https://www.gutenberg.org/cache/epub/98/pg98.txt",
    "The Adventures of Sherlock Holmes (Arthur Conan Doyle)": "https://www.gutenberg.org/cache/epub/1661/pg1661.txt",
    "Dracula (Bram Stoker)": "https://www.gutenberg.org/cache/epub/345/pg345.txt",
    "The Time Machine (H.G. Wells)": "https://www.gutenberg.org/cache/epub/35/pg35.txt"
}

def download_library():
    print("📚 Attempting to acquire texts from Project Gutenberg...")
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, "data", "raw")
    
    os.makedirs(raw_dir, exist_ok=True)
    
    for title, url in BOOKS.items():
        filename = title.split(" (")[0].replace(" ", "_").lower() + ".txt"
        filepath = os.path.join(raw_dir, filename)
        
        if os.path.exists(filepath):
            print(f"   [Exists] {title}")
            continue
            
        print(f"   [Downloading] {title}...")
        try:
            head = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Optional/1.0' } # Gutenberg requires UA often
            response = requests.get(url, headers=head, timeout=10)
            response.raise_for_status()
            
            # Simple cleaning (remove Start/End Project Gutenberg headers roughly)
            text = response.text
            start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
            end_marker = "*** END OF THE PROJECT GUTENBERG EBOOK"
            
            if start_marker in text:
                text = text.split(start_marker)[1]
            if end_marker in text:
                text = text.split(end_marker)[0]
                
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(text.strip())
            print(f"   [Success] Saved to {filename}")
            
        except Exception as e:
            print(f"   [Failed] Could not download {title}: {e}")

if __name__ == "__main__":
    download_library()
