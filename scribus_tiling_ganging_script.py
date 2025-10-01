#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Scribus Tiling/Ganging Script (سكريبت Scribus: ملء الصفحات والإطارات تلقائياً)
"""

import scribus
import os
import sys

# **********************************************
# 1. Helper Functions (الدوال المساعدة)
# **********************************************

def calculate_best_layout(page_w, page_h, frame_w, frame_h, gap_h, gap_v):
    """
    Calculates the best frame orientation (Portrait/Landscape) for maximum density (يحسب أفضل اتجاه للإطارات (رأسي/أفقي) لتحقيق أقصى كثافة)
    
    Now includes gaps in calculations (يشمل المسافات الفاصلة الآن في الحسابات)
    """
    
    # Calculate usable width and height for frames and gaps (حساب العرض والارتفاع القابل للاستخدام للإطارات والفواصل)
    
    # --- Landscape Case (حالة الاتجاه الأفقي) ---
    # Width occupied by a frame in Landscape mode (العرض الذي يشغله إطار واحد في الاتجاه الأفقي) = frame_h
    # Height occupied by a frame in Landscape mode (الارتفاع الذي يشغله إطار واحد في الاتجاه الأفقي) = frame_w
    
    # The calculation structure for number of columns (cols) is: floor((Page_W - Frame_W) / (Frame_W + Gap)) + 1
    
    # Cols: based on Page Width (W) and Rotated Frame Height (H) + H-Gap
    try:
        cols_landscape = int((page_w + gap_h) / (frame_h + gap_h))
    except ZeroDivisionError:
        cols_landscape = 0
        
    # Rows: based on Page Height (H) and Rotated Frame Width (W) + V-Gap
    try:
        rows_landscape = int((page_h + gap_v) / (frame_w + gap_v))
    except ZeroDivisionError:
        rows_landscape = 0
        
    count_landscape = cols_landscape * rows_landscape
    
    
    # --- Portrait Case (حالة الاتجاه الرأسي) ---
    
    # Cols: based on Page Width (W) and Frame Width (W) + H-Gap
    try:
        cols_portrait = int((page_w + gap_h) / (frame_w + gap_h))
    except ZeroDivisionError:
        cols_portrait = 0
        
    # Rows: based on Page Height (H) and Frame Height (H) + V-Gap
    try:
        rows_portrait = int((page_h + gap_v) / (frame_h + gap_v))
    except ZeroDivisionError:
        rows_portrait = 0
        
    count_portrait = cols_portrait * rows_portrait

    # Compare and choose the direction with the largest number of frames (المقارنة واختيار الاتجاه ذو العدد الأكبر من الإطارات)
    if count_portrait >= count_landscape:
        # Best direction is Portrait (No Rotation) (الاتجاه الأفضل هو الرأسي (بدون تدوير))
        return cols_portrait, rows_portrait, frame_w, frame_h, gap_h, gap_v
    else:
        # Best direction is Landscape (90-degree Rotation) (الاتجاه الأفضل هو الأفقي (مع تدوير الإطار 90 درجة))
        # Note: frame_w and frame_h are swapped for actual_frame_w/h (يتم تبديل العرض والارتفاع للإطار الفعلي)
        return cols_landscape, rows_landscape, frame_h, frame_w, gap_h, gap_v


def auto_fill_pages_optimized():
    
    # **********************************************
    # 2. Get User Input (الحصول على مدخلات المستخدم)
    # **********************************************
    
    # 2.1. Image Folder Path (مسار الصور)
    image_dir = scribus.fileDialog('Select Image Folder | اختر مجلد الصور', 'Directories | المجلدات', isdir=True)
    if not image_dir:
        return

    # 2.2. Total Page Dimensions (أبعاد الصفحة الكلية)
    page_width_str = scribus.valueDialog('Page Dimensions | أبعاد الصفحة', 'Enter Total Page Width (mm): | أدخل عرض الصفحة الكلي (مم):', str(210))
    page_height_str = scribus.valueDialog('Page Dimensions | أبعاد الصفحة', 'Enter Total Page Height (mm): | أدخل ارتفاع الصفحة الكلي (مم):', str(297))
    
    try:
        page_width = float(page_width_str)
        page_height = float(page_height_str)
    except ValueError:
        scribus.messageBox("Error | خطأ", "Page dimensions must be numeric values. | يجب إدخال قيم رقمية لأبعاد الصفحة.", scribus.ICON_WARNING, scribus.BUTTON_OK)
        return

    # 2.3. Image Frame Dimensions (أبعاد إطار الصورة)
    frame_width_str = scribus.valueDialog('Frame Dimensions | أبعاد الإطار', 'Enter Desired Frame Width (mm): | أدخل عرض الإطار المطلوب (مم):', str(50))
    frame_height_str = scribus.valueDialog('Frame Dimensions | أبعاد الإطار', 'Enter Desired Frame Height (mm): | أدخل ارتفاع الإطار المطلوب (مم):', str(75))
    
    # 2.4. Frame Gaps (المسافات الفاصلة بين الإطارات - NEW!)
    gap_h_str = scribus.valueDialog('Frame Gaps | المسافات الفاصلة', 'Enter Horizontal Gap Between Frames (mm) [Default: 0]: | أدخل المسافة الأفقية بين الإطارات (مم) [الافتراضي: 0]:', str(0))
    gap_v_str = scribus.valueDialog('Frame Gaps | المسافات الفاصلة', 'Enter Vertical Gap Between Frames (mm) [Default: 0]: | أدخل المسافة الرأسية بين الإطارات (مم) [الافتراضي: 0]:', str(0))

    try:
        frame_width = float(frame_width_str)
        frame_height = float(frame_height_str)
        gap_h = float(gap_h_str)
        gap_v = float(gap_v_str)
    except ValueError:
        scribus.messageBox("Error | خطأ", "All dimensions and gaps must be numeric values. | يجب إدخال قيم رقمية لجميع الأبعاد والمسافات.", scribus.ICON_WARNING, scribus.BUTTON_OK)
        return

    # **********************************************
    # 3. Document Setup and Layout Calculation (إعداد المستند وحساب التخطيط)
    # **********************************************
    
    # 3.1. Calculate Best Layout (حساب أفضل تخطيط)
    # Passing gaps to the calculation function (تمرير المسافات الفاصلة لدالة الحساب)
    cols, rows, actual_frame_w, actual_frame_h, actual_gap_h, actual_gap_v = calculate_best_layout(
        page_width, page_height, frame_width, frame_height, gap_h, gap_v
    )
    frames_per_page = cols * rows

    if frames_per_page == 0:
        scribus.messageBox("Measurement Error | خطأ في القياسات", "No frame can fit on the page with the entered measurements. | لا يمكن احتواء أي إطار في الصفحة بالقياسات المدخلة.", scribus.ICON_WARNING, scribus.BUTTON_OK)
        return
        
    # 3.2. Document Setup (إعداد المستند)
    # Create new document with millimeter units (إنشاء مستند جديد بوحدات المليمترات)
    if not scribus.newDoc((page_width, page_height), (0,0,0,0), scribus.PORTRAIT, 1, scribus.UNIT_MILLIMETERS, scribus.NOFACINGPAGES, scribus.FIRSTPAGERIGHT):
        return

    # **********************************************
    # 4. Image Processing and Generation (معالجة الصور والتوليد)
    # **********************************************
    
    # 4.1. Fetch Images (جلب الصور)
    IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.tif', '.tiff')
    try:
        image_files = sorted([f for f in os.listdir(image_dir) if f.lower().endswith(IMAGE_EXTENSIONS)])
    except Exception as e:
        scribus.messageBox("Folder Error | خطأ في المجلد", f"An error occurred while reading the folder: {e} | حدث خطأ أثناء قراءة المجلد: {e}", scribus.ICON_WARNING, scribus.BUTTON_OK)
        return
        
    if not image_files:
        scribus.messageBox("Notice | تنبيه", "No images found with specified extensions in the folder. | لم يتم العثور على صور بالامتدادات المحددة في المجلد.", scribus.ICON_WARNING, scribus.BUTTON_OK)
        return

    # 4.2. Start Filling Frames (البدء بملء الإطارات)
    total_images = len(image_files)
    current_image_index = 0
    current_page = 1 
    
    while current_image_index < total_images:
        
        # Create a new page after the first page (إنشاء صفحة جديدة بعد الصفحة الأولى)
        if current_page > 1:
            scribus.newPage(-1) 
        
        # Loop to fill frames on the current page (حلقة لملء الإطارات في الصفحة الحالية)
        for r in range(rows):
            for c in range(cols):
                if current_image_index < total_images:
                    
                    # Calculate frame position, including gaps (حساب موقع الإطار، بما في ذلك المسافات الفاصلة)
                    x = c * (actual_frame_w + actual_gap_h)
                    y = r * (actual_frame_h + actual_gap_v)
                    
                    image_filename = image_files[current_image_index]
                    full_path = os.path.join(image_dir, image_filename)

                    # 1. Create Image Frame (إنشاء إطار الصورة)
                    frame = scribus.createImage(x, y, actual_frame_w, actual_frame_h)
                    
                    # 2. Load and Scale Image to Frame (تحميل الصورة وتعديلها لتناسب الإطار)
                    scribus.loadImage(full_path, frame)
                    scribus.setScaleImageToFrame(True, True, frame) # Fit image to frame proportionally (احتواء الصورة في الإطار مع الحفاظ على النسب)
                    
                    # If Landscape layout was chosen (90-degree rotation), rotate the frame (إذا تم اختيار التخطيط الأفقي (تدوير 90 درجة)، نقوم بتدوير الإطار)
                    if actual_frame_w == frame_height and actual_frame_h == frame_width:
                        scribus.rotateObject(90, frame)
                    
                    # 3. Create Transparent Cut Path Frame (إنشاء إطار مسار القطع الشفاف)
                    cut_path_frame = scribus.createRect(x, y, actual_frame_w, actual_frame_h)
                    
                    # Remove Fill Color (إزالة لون التعبئة/الـ Fill)
                    scribus.setFillColor("None", cut_path_frame)
                    
                    # Remove Stroke Color and Line Width (إزالة لون الحدود/الـ Stroke وعرض الخط)
                    scribus.setLineColor("None", cut_path_frame)
                    scribus.setLineWidth(0, cut_path_frame)

                    # If rotation was applied to the image, apply it to the cut path as well (إذا تم تطبيق التدوير على الصورة، قم بتطبيقه على مسار القطع أيضاً)
                    if actual_frame_w == frame_height and actual_frame_h == frame_width:
                        scribus.rotateObject(90, cut_path_frame)
                    
                    current_image_index += 1
                else:
                    break # End of all images (الانتهاء من جميع الصور)

            if current_image_index >= total_images:
                break
                
        current_page += 1
        
    scribus.messageBox("Operation Complete | اكتمال العملية", 
        f"Successfully created {current_page-1} pages and filled {total_images} images. | تم إنشاء {current_page-1} صفحات وتم ملء {total_images} صورة. "
        f"Used {cols} columns and {rows} rows per page. | تم استخدام {cols} عمود و {rows} صف في كل صفحة.", 
        scribus.ICON_INFORMATION, scribus.BUTTON_OK)

if __name__ == '__main__':
    # The script must start with no document open to create a new one (يجب أن يبدأ السكريبت في Scribus بدون مستند مفتوح لإنشاء مستند جديد)
    if not scribus.haveDoc():
        auto_fill_pages_optimized()
    else:
        scribus.messageBox("Alert | تنبيه", "Please close the current document and run the script again to create a new one. | الرجاء إغلاق المستند الحالي وتشغيل السكريبت مرة أخرى لإنشاء مستند جديد.", scribus.ICON_WARNING, scribus.BUTTON_OK)