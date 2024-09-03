import json
import sys
import argparse
from openapi_spec_validator import validate_spec
from urllib.parse import urlparse
from termcolor import colored
import time
import os
import uuid

# ASCII Art
# This script will allow you to convert postman collection into openapi schema required by burp suite
# Fetched from https://github.com/dr34mhacks/Openapi-Schema-Builder

ASCII_ART = """

   ____                   ___    ____  ____    _____      __                               ____        _ __    __         
  / __ \____  ___  ____  /   |  / __ \/  _/   / ___/_____/ /_  ___  ____ ___  ____ _      / __ )__  __(_) /___/ /__  _____
 / / / / __ \/ _ \/ __ \/ /| | / /_/ // /_____\__ \/ ___/ __ \/ _ \/ __ `__ \/ __ `/_____/ __  / / / / / / __  / _ \/ ___/
/ /_/ / /_/ /  __/ / / / ___ |/ ____// /_____/__/ / /__/ / / /  __/ / / / / / /_/ /_____/ /_/ / /_/ / / / /_/ /  __/ /    
\____/ .___/\___/_/ /_/_/  |_/_/   /___/    /____/\___/_/ /_/\___/_/ /_/ /_/\__,_/     /_____/\__,_/_/_/\__,_/\___/_/     
    /_/                                                                                                                   

                                                                                     with <3 by @dr34mhacks                                                                                                                     
"""

def print_ascii_art():
    print(colored(ASCII_ART, 'cyan'))

def display_usage():
    print(colored("Usage: python3 openapi-schema-builder.py -i <input_file> -o <output_file> [--baseurl <base_url>] [--placeholders <placeholders>]", 'yellow'))
    print("\nArguments:")
    print("  -i, --input        Input JSON file (Postman/Swagger)")
    print("  -o, --output       Output OpenAPI JSON file")
    print("  --baseurl          Base URL to replace placeholders in Postman collections")
    print("  --placeholders     Custom placeholders in the format if any (Optional): '{\"id\": \"123\", \"name\": \"Sid\"}'\n")

def detect_schema_type(json_data):
    if "swagger" in json_data:
        return "swagger"
    elif "openapi" in json_data:
        return "openapi"
    elif "info" in json_data and "item" in json_data:
        return "postman"
    else:
        return None

def extract_base_url(postman_schema, user_base_url=None):
    if user_base_url:
        return user_base_url

    base_url = "http://example.com/api"  # Default if no base URL can be determined

    def find_base_url(items):
        for item in items:
            if 'item' in item:
                found_url = find_base_url(item['item'])
                if found_url:
                    return found_url
            elif 'request' in item and 'url' in item['request']:
                url_data = item['request']['url']
                if isinstance(url_data, dict) and 'raw' in url_data:
                    return url_data['raw']
                elif isinstance(url_data, str):
                    return url_data
        return None

    raw_url = find_base_url(postman_schema['item'])
    if raw_url:
        parsed_url = urlparse(raw_url)
        if parsed_url.scheme and parsed_url.netloc:
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    return base_url

def replace_placeholders(url, base_url):
    url = url.replace('{{base_url}}', base_url)
    url = url.replace('{{host}}', base_url)
    return url

def replace_all_placeholders(json_data, base_url):
    def recursive_replace(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key == 'url' and isinstance(value, str):
                    obj[key] = replace_placeholders(value, base_url)
                else:
                    recursive_replace(value)
        elif isinstance(obj, list):
            for i in range(len(obj)):
                recursive_replace(obj[i])
    
    recursive_replace(json_data)
    return json_data

def handle_placeholders(value):
    if value == "<uuid>":
        return str(uuid.uuid4())  # Generate and return a new UUID
    elif value == "<boolean>":
        return False  # Replace <boolean> with False
    elif value == "<string>":
        return "string"
    elif value == "<double>":
        return 0.0
    elif isinstance(value, str) and value.startswith("<") and value.endswith(">"):
        return value.replace("<", "").replace(">", "")  # Simplified placeholder replacement
    return value

def convert_to_schema(data):
    if isinstance(data, dict):
        properties = {}
        for key, value in data.items():
            if isinstance(value, dict):
                properties[key] = convert_to_schema(value)
            elif isinstance(value, list):
                if value:
                    item_schema = convert_to_schema(value[0])
                    properties[key] = {"type": "array", "items": item_schema}
                else:
                    properties[key] = {"type": "array", "items": {"type": "object"}}
            else:
                properties[key] = {"type": type(handle_placeholders(value)).__name__}
        return {"type": "object", "properties": properties}
    elif isinstance(data, list):
        if data:
            item_schema = convert_to_schema(data[0])
            return {"type": "array", "items": item_schema}
        else:
            return {"type": "array", "items": {"type": "object"}}
    return {"type": "string"}

def convert_postman_to_openapi(postman_schema, user_base_url=None, placeholder_map=None):
    base_url = extract_base_url(postman_schema, user_base_url)
    if user_base_url:
        postman_schema = replace_all_placeholders(postman_schema, user_base_url)
    
    openapi_schema = {
        "openapi": "3.0.0",
        "info": {
            "title": postman_schema["info"]["name"],
            "version": "1.0.0"
        },
        "servers": [
            {"url": base_url}
        ],
        "paths": {}
    }

    processed_count = 0
    skipped_count = 0
    skipped_endpoints = []

    def process_item(item):
        nonlocal processed_count, skipped_count
        if 'request' in item and 'url' in item['request']:
            try:
                url_data = item['request']['url']
                if isinstance(url_data, dict):
                    path = "/" + "/".join(url_data.get('path', []))
                elif isinstance(url_data, str):
                    path = urlparse(url_data).path  # Extract path from URL
                else:
                    print(colored(f"Skipping item with unexpected URL format: {item['request']['url']}", 'yellow'))
                    skipped_count += 1
                    skipped_endpoints.append(item['name'])
                    return

                path = replace_placeholders(path, base_url)

                # Replace placeholders with values from the map
                if placeholder_map:
                    for placeholder, value in placeholder_map.items():
                        path = path.replace(placeholder, value)
                
                method = item["request"]["method"].lower()
                
                if not path.startswith('/'):
                    print(colored(f"Skipping item with invalid path: {path}", 'yellow'))
                    skipped_count += 1
                    skipped_endpoints.append(item['name'])
                    return
                
                openapi_schema["paths"].setdefault(path, {})
                
                request_body = None
                if method in ["post", "put", "patch"] and 'body' in item['request']:
                    body = item['request']['body']
                    if 'raw' in body and isinstance(body['raw'], str):
                        try:
                            raw_body = json.loads(body['raw'])
                            request_body = convert_to_schema(raw_body)
                        except json.JSONDecodeError:
                            print(colored(f"Warning: Could not decode body for {item['name']}", 'yellow'))

                openapi_schema["paths"][path][method] = {
                    "summary": item["name"],
                    "responses": {
                        "200": {
                            "description": "Successful operation"
                        }
                    }
                }

                if request_body:
                    openapi_schema["paths"][path][method]["requestBody"] = {
                        "content": {
                            "application/json": {
                                "schema": request_body
                            }
                        }
                    }
                print(colored(f"Processed item with URL: {path}", 'green'))
                processed_count += 1
                
            except Exception as e:
                print(colored(f"Error processing item: {str(e)}", 'red'))
                skipped_count += 1
                skipped_endpoints.append(item['name'])
    
    def process_items(items):
        for item in items:
            if 'item' in item:
                process_items(item['item'])
            else:
                process_item(item)

    process_items(postman_schema["item"])

    # Log skipped endpoints if any
    if skipped_endpoints:
        with open('skipped_endpoints.json', 'w') as skipped_file:
            json.dump(skipped_endpoints, skipped_file, indent=2)
        print(colored(f"\n{skipped_count} endpoints were skipped. Details saved in 'skipped_endpoints.json'.", 'yellow'))

    print(colored(f"\nTotal endpoints processed: {processed_count}", 'green'))
    print(colored(f"Total endpoints skipped: {skipped_count}", 'yellow'))

    return openapi_schema

if __name__ == "__main__":
    print_ascii_art()  # Always display ASCII art at the start, as why not? 

    if len(sys.argv) == 1:
        display_usage()
        sys.exit(0)

    parser = argparse.ArgumentParser(description="Convert Postman or Swagger collections to OpenAPI schema.")
    parser.add_argument("-i", "--input", required=True, help="Input JSON file (Postman/Swagger)")
    parser.add_argument("-o", "--output", required=True, help="Output OpenAPI JSON file")
    parser.add_argument("--baseurl", help="Base URL to replace placeholders in Postman collections")
    parser.add_argument("--placeholders", help="Custom placeholders to replace in format: :placeholder=value, e.g., '{\"id\": \"123\", \"name\": \"Sid\"}'\n")
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output
    base_url = args.baseurl
    placeholder_map = {}

    if args.placeholders:
        placeholder_pairs = args.placeholders.split(',')
        for pair in placeholder_pairs:
            placeholder, value = pair.split('=')
            placeholder_map[placeholder] = value

    try:
        with open(input_file, 'r') as infile:
            json_data = json.load(infile)
            schema_type = detect_schema_type(json_data)
            if schema_type == "postman":
                openapi_schema = convert_postman_to_openapi(json_data, base_url, placeholder_map)
                with open(output_file, 'w') as outfile:
                    json.dump(openapi_schema, outfile, indent=2)
                print(colored(f"OpenAPI schema has been successfully saved to {output_file}.", 'green'))
            else:
                print(colored("Unsupported schema type. Only Postman collections are supported.", 'red'))
    except Exception as e:
        print(colored(f"Error: {str(e)}", 'red'))
