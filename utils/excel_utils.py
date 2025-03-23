"""
Excel utilities for saving ad data with professional formatting
"""
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import logging

def save_ad_to_excel(ad_data: Dict[str, Any]) -> str:
    """
    Save ad data to Excel with professional formatting.
    
    Args:
        ad_data: Dictionary containing ad information
    
    Returns:
        Path to saved Excel file
    """
    try:
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Ensure output directory exists
        os.makedirs("output/excel", exist_ok=True)
        
        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/excel/ad_campaign_{timestamp}.xlsx"
        
        # Prepare data for Excel
        excel_data = prepare_excel_data(ad_data)
        
        # Create Excel writer with XlsxWriter engine for better formatting
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Write the main ad details
            pd.DataFrame([excel_data['main']]).to_excel(writer, sheet_name='Ad Campaign', index=False)
            
            # Write brand analysis separately
            pd.DataFrame([excel_data['brand_analysis']]).to_excel(writer, sheet_name='Brand Analysis', index=False)
            
            # Write social media insights if available
            if 'social_media_insights' in excel_data:
                pd.DataFrame([excel_data['social_media_insights']]).to_excel(
                    writer, sheet_name='Social Media Insights', index=False
                )
            
            # Format worksheets
            format_excel_sheets(writer)
            
        logger.info(f"Ad data saved to Excel: {filename}")
        return filename
    
    except Exception as e:
        logging.error(f"Error saving to Excel: {str(e)}")
        # Create a simple Excel as fallback
        try:
            # Basic fallback
            fallback_filename = f"output/excel/ad_data_fallback_{timestamp}.xlsx"
            pd.DataFrame([{
                'product': ad_data.get('product', 'Unknown'),
                'headline': ad_data.get('headline', ''),
                'subheadline': ad_data.get('subheadline', ''),
                'call_to_action': ad_data.get('call_to_action', ''),
                'image_path': ad_data.get('image_path', '')
            }]).to_excel(fallback_filename, index=False)
            
            return fallback_filename
        except:
            return "Error saving Excel file"

def prepare_excel_data(ad_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Prepare ad data for Excel format by organizing and flattening.
    
    Args:
        ad_data: Raw ad data dictionary
    
    Returns:
        Organized data ready for Excel
    """
    # Main ad information for the first sheet
    main_data = {
        'Campaign Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
        'Product': ad_data.get('product', ''),
        'Brand': ad_data.get('brand_name', ''),
        'Headline': ad_data.get('headline', ''),
        'Subheadline': ad_data.get('subheadline', ''),
        'Body Text': ad_data.get('body_text', ''),
        'Call to Action': ad_data.get('call_to_action', ''),
        'Image Path': ad_data.get('image_path', ''),
        'Base Image Path': ad_data.get('base_image_path', '')
    }
    
    # Process brand analysis
    brand_analysis = {}
    if 'brand_analysis' in ad_data:
        for key, value in ad_data['brand_analysis'].items():
            if isinstance(value, list):
                brand_analysis[f'Brand {key.replace("_", " ").title()}'] = ', '.join(value)
            else:
                brand_analysis[f'Brand {key.replace("_", " ").title()}'] = value
    
    # Process social media insights if available
    social_media_insights = {}
    if 'social_media_insights' in ad_data:
        for key, value in ad_data['social_media_insights'].items():
            if isinstance(value, list):
                social_media_insights[f'SM {key.replace("_", " ").title()}'] = ', '.join(value)
            else:
                social_media_insights[f'SM {key.replace("_", " ").title()}'] = value
    
    return {
        'main': main_data,
        'brand_analysis': brand_analysis,
        'social_media_insights': social_media_insights if social_media_insights else None
    }

def format_excel_sheets(writer) -> None:
    """
    Apply professional formatting to Excel sheets.
    
    Args:
        writer: ExcelWriter object with sheets already written
    """
    # Format each worksheet
    for sheet_name in writer.sheets:
        worksheet = writer.sheets[sheet_name]
        
        # Set column widths
        for idx, col in enumerate(worksheet.columns):
            max_length = 0
            column = col[0].column_letter  # Get column letter
            
            # Find the maximum content length in the column
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            # Set width with some padding
            adjusted_width = max(max_length + 2, 10)
            worksheet.column_dimensions[column].width = min(adjusted_width, 50)
        
        # Format header row
        for cell in worksheet[1]:
            cell.style = 'Headline 4'
            
def export_ad_to_json(ad_data: Dict[str, Any], output_dir: str = "output/json") -> str:
    """
    Export ad data to JSON file.
    
    Args:
        ad_data: Ad data dictionary
        output_dir: Directory to save JSON file
    
    Returns:
        Path to saved JSON file
    """
    import json
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/ad_campaign_{timestamp}.json"
    
    # Save to JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ad_data, f, indent=2, ensure_ascii=False)
    
    return filename

def generate_ad_report(ad_data: Dict[str, Any], output_dir: str = "output/reports") -> str:
    """
    Generate a comprehensive ad report in Excel format.
    
    Args:
        ad_data: Ad data dictionary
        output_dir: Directory to save report
    
    Returns:
        Path to saved report
    """
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Create timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/ad_report_{timestamp}.xlsx"
        
        # Prepare data for different sheets
        campaign_info = {
            'Generation Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'Product': ad_data.get('product', ''),
            'Brand': ad_data.get('brand_name', ''),
            'Industry': ad_data.get('brand_analysis', {}).get('industry', ''),
            'Brand Level': ad_data.get('brand_analysis', {}).get('brand_level', ''),
            'Target Market': ad_data.get('brand_analysis', {}).get('target_market', ''),
        }
        
        ad_content = {
            'Headline': ad_data.get('headline', ''),
            'Subheadline': ad_data.get('subheadline', ''),
            'Body Text': ad_data.get('body_text', ''),
            'Call to Action': ad_data.get('call_to_action', ''),
        }
        
        visual_elements = {
            'Image Path': ad_data.get('image_path', ''),
            'Base Image Path': ad_data.get('base_image_path', ''),
            'Visual Direction': ad_data.get('brand_analysis', {}).get('visual_direction', ''),
            'Color Scheme': ad_data.get('brand_analysis', {}).get('color_scheme', ''),
            'Typography Style': ad_data.get('brand_analysis', {}).get('typography_style', ''),
        }
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Write each section to its own sheet
            pd.DataFrame([campaign_info]).to_excel(writer, sheet_name='Campaign Overview', index=False)
            pd.DataFrame([ad_content]).to_excel(writer, sheet_name='Ad Content', index=False)
            pd.DataFrame([visual_elements]).to_excel(writer, sheet_name='Visual Elements', index=False)
            
            # Write brand analysis if available
            if 'brand_analysis' in ad_data:
                brand_data = {}
                for key, value in ad_data['brand_analysis'].items():
                    if isinstance(value, list):
                        brand_data[key.replace('_', ' ').title()] = ', '.join(value)
                    else:
                        brand_data[key.replace('_', ' ').title()] = value
                
                pd.DataFrame([brand_data]).to_excel(writer, sheet_name='Brand Analysis', index=False)
            
            # Write social media insights if available
            if 'social_media_insights' in ad_data:
                social_data = {}
                for key, value in ad_data['social_media_insights'].items():
                    if isinstance(value, list):
                        social_data[key.replace('_', ' ').title()] = ', '.join(value)
                    else:
                        social_data[key.replace('_', ' ').title()] = value
                
                pd.DataFrame([social_data]).to_excel(writer, sheet_name='Social Media Insights', index=False)
            
            # Format all sheets
            format_excel_sheets(writer)
        
        return filename
    
    except Exception as e:
        logging.error(f"Error generating ad report: {str(e)}")
        return "Error generating report"