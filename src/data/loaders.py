"""Data loading utilities for Doc Assist."""

from pathlib import Path
import json
import pickle


def load_staqc(pickle_path: str):
    """
    Load StaQC data from pickle files.
    
    Args:
        pickle_path: Path to the StaQC pickle file
        
    Returns:
        List of dictionaries with question, code, and qid fields
    """
    try:
        with open(pickle_path, "rb") as f:
            data = pickle.load(f)  # list of (qid, code_snippet, question_title)
        print(f"StaQC data type: {type(data)}")
        print(f"StaQC data length: {len(data)}")
        if len(data) > 0:
            print(f"First item type: {type(data[0])}")
            print(f"First item: {data[0]}")
        result = []
        for item in data:
            try:
                qid, c, q = item
                result.append({"question": q, "code": c, "qid": qid})
            except Exception as e:
                print(f"Error processing StaQC item: {item}, Error: {e}")
        return result
    except Exception as e:
        print(f"Error loading StaQC data: {e}")
        return []


def load_conala(jsonl_path: str):
    """
    Load CoNaLa dataset from JSONL file.
    
    Args:
        jsonl_path: Path to the CoNaLa JSONL file
        
    Returns:
        List of dictionaries with question and code fields
    """
    # expects fields: rewritten_intent, snippet, ...
    try:
        items = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                try:
                    j = json.loads(line)
                    if "rewritten_intent" not in j or "snippet" not in j:
                        print(f"Missing fields in line {i}: {j.keys()}")
                        continue
                    items.append({"question": j["rewritten_intent"], "code": j["snippet"]})
                except Exception as e:
                    print(f"Error processing line {i}: {e}")
        print(f"Loaded {len(items)} items from CoNaLa dataset")
        if len(items) > 0:
            print(f"First item: {items[0]}")
        return items
    except Exception as e:
        print(f"Error loading CoNaLa data: {e}")
        return []
