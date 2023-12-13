import re

def add_space_before(text):
    # Add a space before periods, commas, semicolons, etc.
    processed_text = re.sub(r'([^\s\w])', r' \1', text)
    return processed_text

# Example usage:
input_text = """
In the vibrant town of Academia Springs, there was a college student named Riley Carter who danced through life with a paintbrush in one hand and a heart full of dreams in the other. Riley was a junior majoring in fine arts at Harmony University, where creativity blossomed as freely as the flowers in the campus courtyard. Riley's passion lay in capturing the essence of emotions through vivid and expressive paintings. From the vibrant hues of a sunrise to the subtle shades of a melancholic melody, each stroke of Riley's brush told a unique story. But Riley's artistic journey took an unexpected turn when a call for submissions to the annual Harmony Art Exhibition arrived. Determined to create a masterpiece that would resonate with the theme of "Unity in Diversity," Riley immersed into a whirlwind of inspiration. Late nights turned into early mornings as canvases were filled with scenes depicting people from diverse backgrounds coming together in harmony. The process was both challenging and exhilarating, pushing Riley's artistic boundaries. As the exhibition day approached, Riley felt a mix of excitement and nervousness. The gallery was adorned with an eclectic array of artworks, each telling a different tale of unity and diversity. Riley's painting, titled "Harmony Mosaic," stood out with its vibrant colors and intricate details that celebrated the beauty of differences coming together to create something extraordinary. To Riley's joy, "Harmony Mosaic" received the People's Choice Award at the exhibition, a testament to the emotional impact it had on the viewers. The recognition opened doors for Riley, leading to collaborations with local art communities and invitations to showcase work at various events. Motivated by the success and the desire to give back, Riley initiated art workshops for children in underserved communities. The goal was to inspire young minds to express themselves creatively and discover the joy of art. Riley's passion for fostering unity through art became a driving force in both academic and community endeavors. As graduation day approached, Riley's journey through college became a kaleidoscope of colors and memories. The once-aspiring artist had transformed into a beacon of creativity and inclusivity. The final brushstroke on Riley's college canvas was not just a degree in fine arts but a legacy of spreading love, understanding, and unity through the universal language of art. And so, as Riley stepped into the world beyond college, the canvas of life awaited, ready to be painted with the vibrant strokes of passion, diversity, and the unwavering belief that art has the power to unite hearts and minds.
"""

output_text = add_space_before(input_text)
print(output_text)