#!/usr/bin/env python
"""Script to build FAISS index from documentation data."""

import json
import argparse
import yaml
import numpy as np
from src.data.loaders import load_staqc, load_conala
from src.preprocess.normalize import clean_question, normalize_code
from src.preprocess.chunk import build_corpus
from src.embed.encoder import Embedder
from src.index.build import build_faiss, save_mapping


def main(cfg):
    """
    Main function to build the index.
    
    Args:
        cfg: Configuration dictionary
    """
    # 1) Load data
    records = []
    if cfg["data"]["staqc_path"]:
        print(f"Loading StaQC data from {cfg['data']['staqc_path']}...")
        records += load_staqc(cfg["data"]["staqc_path"])
    if cfg["data"]["conala_path"]:
        print(f"Loading CoNaLa data from {cfg['data']['conala_path']}...")
        records += load_conala(cfg["data"]["conala_path"])
    
    print(f"Loaded {len(records)} total records")
    
    # 2) Build corpus
    print("Building corpus...")
    corpus = build_corpus(records)
    texts = [c["text"] for c in corpus]
    
    # 3) Generate embeddings
    print(f"Generating embeddings using {cfg['embed']['model']}...")
    emb = Embedder(cfg["embed"]["model"]).encode(texts, batch_size=cfg["embed"]["batch_size"])
    emb = emb.astype("float32")
    
    # 4) Build and save index
    print(f"Building {'IVFPQ' if cfg['index']['use_ivfpq'] else 'FlatIP'} index...")
    build_faiss(
        emb, 
        cfg["index"]["faiss_path"],
        cfg["index"]["ivf_centroids"], 
        cfg["index"]["pq_m"],
        cfg["index"]["use_ivfpq"]
    )
    
    # 5) Save mapping
    print(f"Saving mapping to {cfg['index']['mapping_path']}...")
    save_mapping(corpus, cfg["index"]["mapping_path"])
    
    print("Index building complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build FAISS index for Doc Assist")
    parser.add_argument("--config", default="configs/build_index.yaml", help="Path to config file")
    args = parser.parse_args()
    
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)
    
    main(cfg)
