import pandas as pd
import numpy as np
from difflib import SequenceMatcher
import re
import gradio as gr

def find_postal_code_or_location(input_string, num_results, file_path="PLZ_Verzeichnis_OKT25.xlsx"):
    """
    Find postal codes and location names from an Excel file.
    
    Args:
        file_path (str): Path to the Excel file
        input_string (str): Input string to search for
    
    Returns:
        If input is a 4-digit number: location name
        If input is not a number: list of tuples (postal_code, location_name) sorted by similarity
    """
    
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Clean the data - remove rows where PLZ or Ort might be NaN
        df = df.dropna(subset=['PLZ', 'Ort'])
        
        # Convert PLZ to string to handle any potential formatting issues
        df['PLZ'] = df['PLZ'].astype(str).str.strip()
        
        # Check if input is a 4-digit number
        if re.match(r'^\d{4}$', input_string):
            # Convert to integer for matching
            postal_code = int(input_string)
            
            # Find exact match (convert to string for comparison)
            matching_row = df[df['PLZ'].str.strip() == str(postal_code)]
            
            if not matching_row.empty:
                return [[matching_row.iloc[0]['PLZ'],matching_row.iloc[0]['Ort']]]
            else:
                return [['Not found','Not in the data set']]
        
        else:
            # Input is not a 4-digit number, perform fuzzy matching
            input_lower = input_string.lower()
            
            # Calculate similarity scores using SequenceMatcher (which is based on Levenshtein distance)
            def calculate_similarity(name):
                return SequenceMatcher(None, input_lower, name.lower()).ratio()
            
            # Apply similarity calculation to all location names
            df['similarity'] = df['Ort'].apply(calculate_similarity)
            
            # Filter out very low similarities (threshold can be adjusted)
            filtered_df = df[df['similarity'] > 0.1]
            
            # Sort by similarity (descending) and limit to 10 results
            result = filtered_df.sort_values('similarity', ascending=False)[['PLZ', 'Ort']].head(num_results).values.tolist()
            
            return result
            
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")

def get_postal_code(text_in, num_results):
    return find_postal_code_or_location(text_in, num_results)

demo = gr.Interface(
    fn=get_postal_code,
    inputs=["text"],
    additional_inputs=[gr.Slider(value=10, minimum=1, maximum=100, step=1)],
    outputs=[gr.List(
            label="Names", headers=["PLZ", "Ort"],
            show_copy_button=True,
            col_count=2
        )],
)

demo.launch()