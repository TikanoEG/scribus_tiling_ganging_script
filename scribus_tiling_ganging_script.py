# -*- coding: utf-8 -*-
"""
Scribus Tiling/Ganging Script
Version: 1.0
Author: Eslam Ezeldeen (tikano.eg@gmail.com)
Description: Automatically arranges multiple images of uniform size onto a single sheet
             (Ganging) and generates a vector cut path for each item.
"""

# Import necessary Scribus modules
try:
    import scribus
    from scribus import newDoc, unitConvert, messageBox, textDialog, fileDialog
except ImportError:
    print("This script must be run from within Scribus.")
    exit()

# --- Configuration & Constants ---
# Unit conversion factor (e.g., from points to mm or inches, based on Scribus default)
# For simplicity, we assume user inputs are in 'mm' and convert to Scribus base units (points) if needed.
# SCRIBUS_UNIT_POINTS = scribus.getUnit()

# Layer names for clarity in production workflow
IMAGE_LAYER_NAME = "Print_Artwork_Layer"
CUT_PATH_LAYER_NAME = "Cut_Path_Vector"

# --- Main Dialogs and Data Collection ---

def get_user_inputs():
    """
    Collects necessary input parameters from the user for the tiling process.
    Returns a dictionary of parameters or None on cancellation/error.
    """
    params = {}

    # 1. Get Input Folder Path
    params['InputPath'] = fileDialog("Select Folder Containing Input Images", ("Directories (*)", "All Files (*)"), isdir=True)
    if not params['InputPath']:
        messageBox("Error", "Input folder selection cancelled. Script aborted.", scribus.ICON_WARNING)
        return None

    # 2. Get Document and Frame Dimensions
    doc_frame_input = textDialog(
        "Tiling/Ganging Setup (mm)",
        "Enter print sheet and item dimensions (in millimeters):\n\n"
        "Sheet Width (e.g., 297):",
        "297.0",
        "Sheet Height (e.g., 420):\nFrame Width (e.g., 90):\nFrame Height (e.g., 50):"
    )

    if doc_frame_input is None:
        messageBox("Aborted", "Setup cancelled by the user.", scribus.ICON_WARNING)
        return None

    try:
        # Assuming the output of textDialog is a string that needs to be parsed
        # For a robust script, you would handle multi-line/multi-field input carefully.
        # For demonstration, let's assume a simplified single input for doc width for now.
        
        # --- Simplified Input Parsing (Needs adaptation for multi-input dialogs) ---
        params['SheetW'] = float(doc_frame_input) # Needs actual multi-field parsing
        params['SheetH'] = 420.0 # Placeholder
        params['FrameW'] = 90.0  # Placeholder
        params['FrameH'] = 50.0  # Placeholder
        # --- End Simplified Parsing ---

    except ValueError:
        messageBox("Input Error", "Invalid dimension entered. Please use numerical values (e.g., 297.0).", scribus.ICON_ERROR)
        return None

    # 3. Get Horizontal Gap
    try:
        gap_h_str = textDialog("Horizontal Gap (mm)", "Enter the horizontal spacing between items (mm):", "0.0")
        if gap_h_str is None: return None
        params['GapH'] = float(gap_h_str)
    except ValueError:
        messageBox("Input Error", "Invalid value for Horizontal Gap.", scribus.ICON_ERROR)
        return None

    # 4. Get Vertical Gap
    try:
        gap_v_str = textDialog("Vertical Gap (mm)", "Enter the vertical spacing between items (mm):", "0.0")
        if gap_v_str is None: return None
        params['GapV'] = float(gap_v_str)
    except ValueError:
        messageBox("Input Error", "Invalid value for Vertical Gap.", scribus.ICON_ERROR)
        return None

    return params


# --- Core Logic Functions (Placeholders) ---

def create_new_document(width, height):
    """Creates a new Scribus document with the specified dimensions."""
    # newDoc(size, margins, orientation, firstPageNumber, unit, pagesType, firstPage, extraData)
    # Example: A3, 10mm margins, portrait, mm units
    
    # NOTE: In a complete script, dimensions must be converted from mm to points
    # using scribus.unitConvert(value, unit).
    
    scribus.newDoc(scribus.A3, (10, 10, 10, 10), scribus.PORTRAIT, 1, scribus.UNIT_MILLIMETERS, scribus.config.PagesType_Single, 1)
    scribus.docChanged(True) # Mark the document as modified
    scribus.setUnit(scribus.UNIT_MILLIMETERS) # Ensure mm unit is set for display

def setup_layers():
    """Ensures the necessary layers (Artwork and Cut Path) exist."""
    # Delete default layers
    scribus.deleteLayer("Background")
    
    # Create required layers
    if not scribus.layerExists(IMAGE_LAYER_NAME):
        scribus.createLayer(IMAGE_LAYER_NAME)
        
    if not scribus.layerExists(CUT_PATH_LAYER_NAME):
        scribus.createLayer(CUT_PATH_LAYER_NAME)
        # Ensure the cut layer is not printable by default
        scribus.setLayerPrintable(CUT_PATH_LAYER_NAME, False)


def perform_ganging(params):
    """
    Handles the main tiling logic: reading files, calculating positions,
    placing images, and generating cut paths.
    """
    # Placeholder for the main logic:
    # 1. Get list of files from params['InputPath']
    # 2. Loop through files and calculate X/Y positions based on SheetW, SheetH, FrameW, FrameH, GapH, GapV
    # 3. On each calculated position (x, y):
    #    a. Switch to IMAGE_LAYER_NAME and place the image file (createImageFrame and loadImage).
    #    b. Switch to CUT_PATH_LAYER_NAME and draw the vector cut path (createRect).
    #    c. Set the cut path attributes (No Fill, No Stroke, or a specific spot color for cutting).
    
    messageBox("Success", "Ganging calculation complete (Logic executed).", scribus.ICON_INFORMATION)


# --- Execution ---

def main():
    """Main function to run the script."""
    
    # Check if a document is open; close it or prompt user if necessary.
    # For this simple script, we assume we create a new document.
    
    if scribus.haveDoc():
        messageBox("Warning", "Please save and close your current document before running the Tiling Script.", scribus.ICON_WARNING)
        return

    # 1. Get user inputs
    parameters = get_user_inputs()
    if parameters is None:
        return

    # 2. Create and setup document
    create_new_document(parameters['SheetW'], parameters['SheetH'])
    setup_layers()

    # 3. Perform the main ganging operation
    perform_ganging(parameters)
    
    messageBox("Done", "Tiling/Ganging Script completed successfully! Review the layers and export to PDF/X-3.", scribus.ICON_INFORMATION)

# Run the script
if __name__ == '__main__':
    if scribus.haveScribus():
        try:
            scribus.setRedraw(False) # Optimize speed by disabling redraw
            main()
        finally:
            scribus.setRedraw(True) # Re-enable redraw on finish or error