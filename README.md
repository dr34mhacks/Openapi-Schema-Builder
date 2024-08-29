<h1 align="center"><img src="https://github.com/user-attachments/assets/8a908adf-fb4d-45a2-872d-59e3a65de835"></h1>


<p align="center">
  <a href="#about">📖 About</a> •
  <a href="#-features">🚀 Features</a> •
  <a href="#-installation">🎯 Installation</a> •
  <a href="#-usage">🛠 Usage</a> •
  <a href="#-integration-with-burp-suite">🌟 Integration with Burp Suite</a> •
  <a href="#-contributing">🤝 Contributing</a> •
</p>

# About

The OpenAPI Schema Builder is a simple tool designed to transform Postman collections and Swagger schemas into OpenAPI definitions. This is especially useful for integrating API documentation with tools like **Burp Suite**, which require OpenAPI schemas instead of Postman collections. The tool also supports custom placeholder replacement, making it adaptable for various API endpoint patterns.

## 🚀 Features

- **Seamless Conversion**: Effortlessly convert Postman collections and Swagger files to OpenAPI 3.0 format.
- **Placeholder Handling**: Replace placeholders and base URLs in Postman collections for accurate API endpoints.
- **Schema Validation**: Automatically validate your OpenAPI schema against the OpenAPI specification to ensure correctness.
- **Comprehensive Output**: Generate a detailed OpenAPI schema file and track skipped endpoints in a dedicated log file.
- **User-Friendly Interface**: Enjoy colorful and informative terminal output to track progress and issues.
- **Burp Suite Integration**: Easily convert Postman collections to OpenAPI schemas to integrate with Burp Suite's new feature for API documentation upload.

## 🎯 Installation

To Install `OpenAPI-Schema-Builder`, follow these steps:

```bash
git clone https://github.com/dr34mhacks/Openapi-Schema-Builder.git
cd Openapi-Schema-Builder
pip3 install -r requirements.txt
```

To use the OpenAPI Schema Converter, run the script with the following command:

```bash
python3 converter.py -i <input_file> -o <output_file> --baseurl <base_url>
```
<img width="1635" alt="image" src="https://github.com/user-attachments/assets/e13f2f3f-7e55-4a69-a415-9ee898fcb972">

**Parameters:**

- `-i`, `--input`: Path to your input JSON file (Postman or Swagger format).
- `-o`, `--output`: Path where the converted OpenAPI JSON file will be saved.
- `--baseurl`: Base URL to replace placeholder of base_url or API Host in Postman collections.
- `--placeholders`: Optional. Custom placeholder replacements in the format `'{"key1": "value1", "key2": "value2"}'`.

## 🛠 Usage

Created a dummy simple postman collection for the demo purpose. 

<details>
 <summary>input.json</summary>
 <pre>

```json
{
    "info": {
        "name": "Dummy API",
        "description": "A dummy Postman collection with placeholders in URL endpoints.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "Get User",
            "request": {
                "method": "GET",
                "url": {
                    "raw": "{{base_url}}/users/:id",
                    "host": [
                        "{{base_url}}"
                    ],
                    "path": [
                        "users",
                        ":id"
                    ]
                }
            },
            "response": []
        },
        {
            "name": "Create User",
            "request": {
                "method": "POST",
                "url": {
                    "raw": "{{base_url}}/users",
                    "host": [
                        "{{base_url}}"
                    ],
                    "path": [
                        "users"
                    ]
                },
                "body": {
                    "mode": "raw",
                    "raw": "{ \"name\": \"John Doe\", \"email\": \"john@example.com\" }"
                }
            },
            "response": []
        },
        {
            "name": "Update User",
            "request": {
                "method": "PUT",
                "url": {
                    "raw": "{{base_url}}/users/:id",
                    "host": [
                        "{{base_url}}"
                    ],
                    "path": [
                        "users",
                        ":id"
                    ]
                },
                "body": {
                    "mode": "raw",
                    "raw": "{ \"name\": \"Jane Doe\", \"email\": \"jane@example.com\" }"
                }
            },
            "response": []
        },
        {
            "name": "Delete User",
            "request": {
                "method": "DELETE",
                "url": {
                    "raw": "{{base_url}}/users/:id",
                    "host": [
                        "{{base_url}}"
                    ],
                    "path": [
                        "users",
                        ":id"
                    ]
                }
            },
            "response": []
        },
        {
            "name": "Get User by Name",
            "request": {
                "method": "GET",
                "url": {
                    "raw": "{{base_url}}/users/name/:name",
                    "host": [
                        "{{base_url}}"
                    ],
                    "path": [
                        "users",
                        "name",
                        ":name"
                    ]
                }
            },
            "response": []
        }
    ]
}
```
</pre>
</details>

To replace `:id` and `:name` placeholders, run the script with the following command:

```bash
python3 openapi-schema-builder.py -i input.json -o output.json --baseurl "http://api.example.com" --placeholders '{"id": "123", "name": "John"}'
```

<img width="1635" alt="image" src="https://github.com/user-attachments/assets/b91da339-1e18-4700-b6ca-3df7e6c46bd9">


This command reads `input.json`, replaces `{{base_url}}` with `https://api.example.com`, and outputs the result to `output.json`.

## 🌟 Integration with Burp Suite

Burp Suite now introduces a feature that allows uploading API documentation directly to the scanner. However, Burp Suite requires the documentation to be in OpenAPI schema format, rather than just Postman collections.

This tool bridges the gap by converting Postman collections to OpenAPI schemas, enabling smooth integration with Burp Suite’s new API documentation upload feature. Enhance your API security testing with Burp Suite by ensuring your Postman collections are readily available in OpenAPI format.

### Uploading `output.json` file to Burp API Scan under the `Dashboard` tab

<img width="1635" alt="image" src="https://github.com/user-attachments/assets/26005301-deb1-4540-bc6f-a5c4ebbb1ae6">

### Running API Scan 

<img width="1635" alt="image" src="https://github.com/user-attachments/assets/638fc4c5-5f8d-4b47-8f05-a592aae27857">

## 🤝 Contributing

We welcome contributions! If you have ideas for improvements or bug fixes, please fork the repository and submit a pull request. Make sure to include tests and documentation for any changes.

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

Happy Hacking 🥷
