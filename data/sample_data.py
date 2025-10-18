"""Script to generate sample data for testing."""

import pickle
import json
import os
from pathlib import Path

# Create sample StaQC data
sample_staqc = [
    (1, "def example():\n    return 'Hello'", "How to create a simple function?"),
    (2, "import numpy as np\n\narr = np.array([1, 2, 3])", "How to create a numpy array?"),
    (3, "for i in range(10):\n    print(i)", "How to loop through numbers?"),
    (4, "import pandas as pd\n\ndf = pd.read_csv('file.csv')", "How to read a CSV file with pandas?"),
    (5, "import pandas as pd\n\ndf = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})\ndf.groupby('A').sum()", "How to groupby and sum in pandas?")
]

# Create sample CoNaLa data
sample_conala = [
    {
        "rewritten_intent": "create a list of integers from 1 to 10",
        "snippet": "list(range(1, 11))"
    },
    {
        "rewritten_intent": "get the current date",
        "snippet": "from datetime import date\ntoday = date.today()"
    },
    {
        "rewritten_intent": "read a file line by line",
        "snippet": "with open('file.txt', 'r') as f:\n    lines = f.readlines()"
    },
    {
        "rewritten_intent": "sort a list in descending order",
        "snippet": "x = [3, 1, 2]\nx.sort(reverse=True)"
    },
    {
        "rewritten_intent": "convert a string to lowercase",
        "snippet": "text = 'Hello World'\nlower_text = text.lower()"
    }
]

def main():
    """Generate and save sample data files."""
    data_dir = Path(__file__).parent
    
    # Save StaQC sample
    staqc_path = data_dir / "staqc_python.pkl"
    with open(staqc_path, "wb") as f:
        pickle.dump(sample_staqc, f)
    print(f"Saved sample StaQC data to {staqc_path}")
    
    # Save CoNaLa sample
    conala_dir = data_dir / "conala"
    conala_dir.mkdir(exist_ok=True)
    
    conala_path = conala_dir / "conala-train.jsonl"
    with open(conala_path, "w") as f:
        for item in sample_conala:
            f.write(json.dumps(item) + "\n")
    print(f"Saved sample CoNaLa data to {conala_path}")

if __name__ == "__main__":
    main()
