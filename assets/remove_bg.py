#!/usr/bin/env python3
"""Remove background from images using rembg."""

import sys
import os
from rembg import remove
from PIL import Image

def remove_bg(input_path, output_path):
    print(f"Processing: {input_path}")
    
    with open(input_path, 'rb') as f:
        input_data = f.read()
    
    output_data = remove(input_data)
    
    with open(output_path, 'wb') as f:
        f.write(output_data)
    
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 remove_bg.py <input.png> <output.png>")
        sys.exit(1)
    
    remove_bg(sys.argv[1], sys.argv[2])