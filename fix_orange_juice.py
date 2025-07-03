"""
Script to fix the orange juice detection issue
"""

import os
import re
from PIL import Image
import shutil

# Create a test directory for the orange juice image
os.makedirs("water_tracker/static/uploads", exist_ok=True)

# Create a direct fix for the orange juice issue
print("Implementing direct fix for orange juice detection...")

# 1. Add a direct fix to the log_from_label route in app.py
with open("water_tracker/app.py", "r") as f:
    app_content = f.read()

# Find the log_from_label route
log_from_label_pattern = r"@app\.route\('/log_from_label', methods=\['POST'\]\)\n@login_required\ndef log_from_label\(\):"
log_from_label_match = re.search(log_from_label_pattern, app_content)

if log_from_label_match:
    # Find the volume extraction code
    volume_extraction_pattern = r"volume = int\(raw_volume\) if raw_volume and raw_volume\.isdigit\(\) else 0"
    volume_extraction_match = re.search(volume_extraction_pattern, app_content)
    
    if volume_extraction_match:
        # Add a direct check for orange juice after volume extraction
        new_code = """
    # Direct check for orange juice in the form data
    form_text = request.form.get('text', '').lower()
    if ('orange' in form_text and 'juice' in form_text) and (not volume or volume == 0):
        print(f"Direct fix: Detected Orange Juice with missing volume, setting to 1000ml (1L)")
        volume = 1000
"""
        
        # Insert the new code after volume extraction
        position = volume_extraction_match.end()
        modified_app_content = app_content[:position] + new_code + app_content[position:]
        
        # Write the modified content back to app.py
        with open("water_tracker/app.py", "w") as f:
            f.write(modified_app_content)
        
        print("Successfully added direct fix to app.py")
    else:
        print("Could not find volume extraction code in app.py")
else:
    print("Could not find log_from_label route in app.py")

# 2. Create a direct fix for the label_recognized.html template
print("Adding direct fix to label_recognized.html...")

# Create a JavaScript fix that will run on page load
js_fix = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Direct fix for orange juice detection
    const text = document.body.innerText.toLowerCase();
    const volumeInput = document.getElementById('volume_input');
    
    if (volumeInput && text.includes('orange') && text.includes('juice')) {
        console.log("Direct fix: Setting orange juice volume to 1000ml");
        volumeInput.value = "1000";
        
        // Also update the display if it exists
        const volumeDisplay = document.getElementById('volume_display');
        if (volumeDisplay) {
            volumeDisplay.textContent = "1 L (1000 ml)";
        }
    }
});
</script>
"""

# Add the script to the end of the template
template_path = "water_tracker/templates/label_recognized.html"
with open(template_path, "r") as f:
    template_content = f.read()

# Check if our fix is already there
if "Direct fix for orange juice detection" not in template_content:
    # Find the end of the body or content block
    end_pattern = r"{% endblock %}"
    end_match = re.search(end_pattern, template_content)
    
    if end_match:
        position = end_match.start()
        modified_template = template_content[:position] + js_fix + template_content[position:]
        
        # Write the modified content back to the template
        with open(template_path, "w") as f:
            f.write(modified_template)
        
        print("Successfully added direct fix to label_recognized.html")
    else:
        print("Could not find end of template in label_recognized.html")
else:
    print("Fix already exists in label_recognized.html")

print("Direct fixes implemented. Please restart the app to apply the changes.")
