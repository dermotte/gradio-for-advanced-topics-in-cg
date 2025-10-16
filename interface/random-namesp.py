import random
import gradio as gr

def generate_random_names(pattern, count=10):
    """
    Generate random names based on a pattern of vowels and consonants.
    
    Args:
        pattern (str): Pattern string where 'v' = vowel, 'c' = consonant
        count (int): Number of names to generate (default: 10)
    
    Returns:
        list: List of random names following the specified pattern
    
    Example:
        generate_random_names('vccv', 5)  # Generates 5 names like "Mira", "Lena"
    """
    
    # Define vowels and consonants
    vowels = ['a', 'e', 'i', 'o', 'u']
    consonants = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 
                  'n', 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z']
    
    names = []
    
    for _ in range(count):
        name = ""
        for char in pattern.lower():
            if char == 'v':
                name += random.choice(vowels)
            elif char == 'c':
                name += random.choice(consonants)
            else:
                # Handle invalid characters (optional)
                raise ValueError(f"Invalid character '{char}' in pattern. Use only 'v' or 'c'.")
        
        names.append(name[0].upper() + name[1:])
    
    return names

# Extended Gradio Interface, Step 5
input_dropdown = gr.Dropdown(
            label="Pattern",
            info="Provide a Pattern string where 'v' = vowel, 'c' = consonant",
            allow_custom_value=True,
            choices=["vcc", "ccv", "vccv","cvcc","ccvc",  "cvccv", "ccvcc",  "vccvc",   "cvccvc",  "vccvcc",  "cvccvcc"]
        )
output_text = gr.List(
            label="Names", headers=None,
            show_copy_button=True,
            col_count=1
        )
demo = gr.Interface(
    fn=generate_random_names,
    inputs=[input_dropdown],
    additional_inputs=[gr.Slider(value=10, minimum=1, maximum=100, step=1)],
    outputs=[output_text],
    flagging_mode="never",
    theme="ocean"
)

demo.launch()