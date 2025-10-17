import pandas as pd
import numpy as np
from difflib import SequenceMatcher
import re
import gradio as gr

"""
Postal Code and Location Finder for Austria

This Gradio application allows users to find postal codes and location names for Austria.
It provides two search modes:
1. Exact search: Enter a 4-digit postal code to get the corresponding location name
2. Fuzzy search: Enter a location name to find matching postal codes (with similarity matching)

The application uses data from PLZ_Verzeichnis_OKT25.xlsx which contains Austrian postal codes and locations.
"""

def find_postal_code_or_location(input_string, num_results, file_path="PLZ_Verzeichnis_OKT25.xlsx"):
    """
    Find postal codes and location names from an Excel file based on user input.
    
    This function supports two search modes:
    - Exact search: If input is a 4-digit number, it performs an exact match against postal codes
    - Fuzzy search: If input is text, it performs similarity matching against location names
    
    Args:
        input_string (str): The search query (postal code or location name)
        num_results (int): Number of results to return (for fuzzy search)
        file_path (str): Path to the Excel file containing postal code data (default: "PLZ_Verzeichnis_OKT25.xlsx")
    
    Returns:
        list: List of results in format [[postal_code, location_name], ...]
              For exact match: single result or 'Not found' if no match
              For fuzzy search: up to num_results sorted by similarity score
              
    Example:
        Input: "1010" -> Returns: [["1010", "Wien"]]
        Input: "wien" -> Returns: List of locations similar to "wien" sorted by similarity
    """
    
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Clean the data - remove rows where PLZ or Ort might be NaN
        df = df.dropna(subset=['PLZ', 'Ort'])
        
        # Convert PLZ to string to handle any potential formatting issues
        df['PLZ'] = df['PLZ'].astype(str).str.strip()
        
        # Check if input is a 4-digit number (exact postal code search)
        if re.match(r'^\d{4}$', input_string):
            # Convert to integer for matching
            postal_code = int(input_string)
            
            # Find exact match (convert to string for comparison)
            matching_row = df[df['PLZ'].str.strip() == str(postal_code)]
            
            if not matching_row.empty:
                return [[matching_row.iloc[0]['PLZ'], matching_row.iloc[0]['Ort']]]
            else:
                return [['Not found', 'Not in the data set']]
        
        else:
            # Input is not a 4-digit number, perform fuzzy matching (location name search)
            input_lower = input_string.lower()
            
            # Calculate similarity scores using SequenceMatcher (which is based on Levenshtein distance)
            def calculate_similarity(name):
                return SequenceMatcher(None, input_lower, name.lower()).ratio()
            
            # Apply similarity calculation to all location names
            df['similarity'] = df['Ort'].apply(calculate_similarity)
            
            # Filter out very low similarities (threshold can be adjusted)
            filtered_df = df[df['similarity'] > 0.1]
            
            # Sort by similarity (descending) and limit to num_results
            result = filtered_df.sort_values('similarity', ascending=False)[['PLZ', 'Ort']].head(num_results).values.tolist()
            
            return result
            
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")


def get_postal_code(text_in, num_results):
    """
    Wrapper function to call find_postal_code_or_location with appropriate parameters.
    
    Args:
        text_in (str): The search query (postal code or location name)
        num_results (int): Number of results to return for fuzzy search
    """
    return find_postal_code_or_location(text_in, num_results)


# Create the Gradio interface
demo = gr.Interface(
    fn=get_postal_code,
    inputs=["text"],
    additional_inputs=[gr.Slider(value=10, minimum=1, maximum=100, step=1, label="Number of Results")],
    outputs=[gr.List(
            label="Results", headers=["PLZ", "Ort"],
            show_copy_button=True,
            col_count=2
        )],
    title="Austrian Postal Code Finder",
    description="Enter a 4-digit postal code for exact match or a location name for fuzzy search. Results are sorted by relevance.",
)

demo.launch()
