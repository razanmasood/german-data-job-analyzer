"""
HTML parsing utilities for job descriptions.
Properly handles spacing between HTML elements to avoid concatenated words.
"""

from bs4 import BeautifulSoup
import re


def clean_html_description(html_text: str) -> str:
    """
    Parse HTML job description and convert to clean text with proper spacing.
    
    Handles:
    - Block elements (p, div, li) → Add newlines
    - Line breaks (br) → Add newlines  
    - Inline formatting (strong, em) → Preserve with spaces
    - Multiple whitespace → Collapse to single space
    
    Args:
        html_text: Raw HTML from descriptionHtml field
        
    Returns:
        Clean text with proper word boundaries
        
    Example:
        Input:  "<p>Python</p><p>SQL</p>"
        Output: "Python\nSQL"  (not "PythonSQL")
    """
    if not html_text:
        return ""
    
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # Remove script and style elements completely
    for element in soup(['script', 'style', 'button', 'icon']):
        element.decompose()
    
    # Add newlines before/after block elements
    for element in soup.find_all(['p', 'div', 'li', 'ul', 'ol', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        element.insert_before('\n')
        element.insert_after('\n')
    
    # Convert br tags to newlines
    for br in soup.find_all('br'):
        br.replace_with('\n')
    
    # Get text with space separator for inline elements
    text = soup.get_text(separator=' ')
    
    # Clean up whitespace
    # 1. Replace multiple spaces with single space
    text = re.sub(r' +', ' ', text)
    
    # 2. Replace multiple newlines with double newline (paragraph breaks)
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    
    # 3. Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(lines)
    
    # 4. Remove empty lines
    text = '\n'.join(line for line in text.split('\n') if line)
    
    return text.strip()


def test_html_parser():
    """Test the HTML parser with example cases."""
    
    test_cases = [
        # Case 1: Block elements without spacing
        ("<p>Python</p><p>SQL</p>", "Python\nSQL"),
        
        # Case 2: Break tags
        ("Experience with<br/>Python<br/>and SQL", "Experience with\nPython\nand SQL"),
        
        # Case 3: List items
        ("<ul><li>Python</li><li>SQL</li></ul>", "Python\nSQL"),
        
        # Case 4: Strong tags (inline)
        ("<strong>Python</strong> and <strong>SQL</strong>", "Python and SQL"),
        
        # Case 5: Mixed content
        ("<p>Requirements:</p><ul><li>Python</li><li>SQL</li></ul>", 
         "Requirements:\nPython\nSQL"),
    ]
    
    print("Testing HTML parser...")
    for i, (html_input, expected) in enumerate(test_cases, 1):
        result = clean_html_description(html_input)
        # Normalize whitespace for comparison
        result_normalized = ' '.join(result.split())
        expected_normalized = ' '.join(expected.split())
        
        if result_normalized == expected_normalized:
            print(f"✓ Test {i} passed")
        else:
            print(f"✗ Test {i} failed")
            print(f"  Expected: {expected_normalized}")
            print(f"  Got:      {result_normalized}")
    
    print("\nDone!")


if __name__ == "__main__":
    test_html_parser()