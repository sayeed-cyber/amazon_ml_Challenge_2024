import csv
import re
import requests
from PIL import Image
from io import BytesIO
import easyocr
import time
from itertools import islice

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Define the entity_unit_map (unchanged)
entity_unit_map = {
    'width': {'centimetre', 'foot', 'inch', 'metre', 'millimetre', 'yard'},
    'depth': {'centimetre', 'foot', 'inch', 'metre', 'millimetre', 'yard'},
    'height': {'centimetre', 'foot', 'inch', 'metre', 'millimetre', 'yard'},
    'item_weight': {'gram', 'kilogram', 'microgram', 'milligram', 'ounce', 'pound', 'ton'},
    'maximum_weight_recommendation': {'gram', 'kilogram', 'microgram', 'milligram', 'ounce', 'pound', 'ton'},
    'voltage': {'kilovolt', 'millivolt', 'volt'},
    'wattage': {'kilowatt', 'watt'},
    'item_volume': {'centilitre', 'cubic foot', 'cubic inch', 'cup', 'decilitre', 'fluid ounce', 'gallon', 'imperial gallon', 'litre', 'microlitre', 'millilitre', 'pint', 'quart'}
}

# Create a set of all allowed units
allowed_units = {unit for entity in entity_unit_map for unit in entity_unit_map[entity]}

# Expanded mapping of unit abbreviations to full unit names (unchanged)
unit_abbreviations = {
    # Length
    'cm': 'centimetre', 'centimeter': 'centimetre', 'cms': 'centimetre', 'cm.': 'centimetre',
    'ft': 'foot', 'feet': 'foot',
    'in': 'inch', 'inches': 'inch', 'in.': 'inch',
    'm': 'metre', 'meter': 'metre', 'meters': 'metre', 'm.': 'metre',
    'mm': 'millimetre', 'millimeter': 'millimetre', 'mm.': 'millimetre', 'MM': 'millimetre',
    'yd': 'yard', 'yards': 'yard',

    # Weight
    'g': 'gram', 'grams': 'gram', 'gm': 'gram', 'gms': 'gram', 'g.': 'gram',
    'kg': 'kilogram', 'kilograms': 'kilogram', 'kgs': 'kilogram', 'kg.': 'kilogram',
    'mg': 'milligram', 'milligrams': 'milligram', 'mgs': 'milligram', 'mg.': 'milligram',
    'μg': 'microgram', 'microgram': 'microgram',
    'oz': 'ounce', 'ounces': 'ounce', 'oz.': 'ounce',
    'lb': 'pound', 'pounds': 'pound', 'lbs': 'pound', 'lb.': 'pound',

    # Voltage
    'kv': 'kilovolt', 'kv.': 'kilovolt',
    'mv': 'millivolt',
    'v': 'volt', 'volts': 'volt', 'v.': 'volt',

    # Power
    'kw': 'kilowatt', 'kw.': 'kilowatt',
    'w': 'watt', 'watts': 'watt', 'w.': 'watt',

    # Volume
    'cl': 'centilitre', 'centiliter': 'centilitre',
    'ml': 'millilitre', 'milliliter': 'millilitre', 'ml.': 'millilitre',
    'l': 'litre', 'L': 'litre', 'liters': 'litre', 'l.': 'litre',
    'gal': 'gallon', 'gallons': 'gallon', 'gal.': 'gallon',
    'pt': 'pint', 'pints': 'pint', 'pt.': 'pint',
    'qt': 'quart', 'quarts': 'quart', 'qt.': 'quart',

    # Fluid Volume
    'fl oz': 'fluid ounce', 'fl. oz.': 'fluid ounce', 'floz': 'fluid ounce',

    # Additional Unit Forms
    'mL': 'millilitre', 'Kg': 'kilogram', 'G': 'gram'
}

def process_image_from_url(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        results = reader.readtext(image)
        recognized_text = ' '.join([result[1] for result in results])
        return recognized_text
    except Exception as e:
        print(f"Error processing image {image_url}: {e}")
        return None

def extract_measurement(text, entity_name):
    pattern = r'(\d+(?:\.\d+)?)\s*([a-zA-Z]+)'
    matches = re.findall(pattern, text, re.IGNORECASE)

    for value, unit in matches:
        unit_lower = unit.lower()
        full_unit = next((v for k, v in unit_abbreviations.items() if k == unit_lower), unit_lower)

        if full_unit in entity_unit_map.get(entity_name, set()):
            formatted_value = f"{float(value):.2f}".rstrip('0').rstrip('.')
            return f"{formatted_value} {full_unit}"

    return None

def predict_likely_measurement(entity_name):
    if entity_name in ['width', 'depth', 'height']:
        return "10.00 centimetre"
    elif entity_name in ['item_weight', 'maximum_weight_recommendation']:
        return "1.00 kilogram"
    elif entity_name == 'voltage':
        return "220.00 volt"
    elif entity_name == 'wattage':
        return "100.00 watt"
    elif entity_name == 'item_volume':
        return "1.00 litre"
    else:
        return "N/A"

def process_images_from_csv(input_csv, output_csv, not_found_csv, batch_size=100):
    with open(input_csv, 'r', encoding='utf-8') as csvfile, \
         open(output_csv, 'w', newline='', encoding='utf-8') as outfile, \
         open(not_found_csv, 'w', newline='', encoding='utf-8') as not_found_file:
        reader = csv.DictReader(csvfile)
        writer = csv.writer(outfile)
        not_found_writer = csv.writer(not_found_file)

        writer.writerow(['index', 'prediction'])
        not_found_writer.writerow(['index', 'image_link', 'group_id', 'entity_name'])

        batch_num = 1
        while True:
            start_time = time.time()
            batch = list(islice(reader, batch_size))
            if not batch:
                break

            for row in batch:
                index = row['index']
                image_url = row['image_link']
                group_id = row['group_id']
                entity_name = row['entity_name']

                extracted_text = process_image_from_url(image_url)
                if extracted_text:
                    measurement = extract_measurement(extracted_text, entity_name)
                    if measurement:
                        writer.writerow([index, measurement])
                    else:
                        print(f"No valid measurement found for {image_url}")
                        print(f"Extracted text: {extracted_text}")
                        likely_measurement = predict_likely_measurement(entity_name)
                        writer.writerow([index, likely_measurement])
                        not_found_writer.writerow([index, image_url, group_id, entity_name])
                else:
                    print(f"Failed to extract text from {image_url}")
                    likely_measurement = predict_likely_measurement(entity_name)
                    writer.writerow([index, likely_measurement])
                    not_found_writer.writerow([index, image_url, group_id, entity_name])

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Batch {batch_num} processed in {elapsed_time:.2f} seconds")
            batch_num += 1

# Example usage
input_csv = 'non1.csv'  # Replace with your input CSV file path
output_csv = 'oo1.csv'  # Replace with your desired output CSV file path
not_found_csv = 'not_found.csv'  # CSV file for logging cases with no valid measurement
process_images_from_csv(input_csv, output_csv, not_found_csv)