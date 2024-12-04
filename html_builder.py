# html_builder.py

import os

import os
import webbrowser

def generate_html_for_screenshots(record):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    timestamp = record['timestamp']
    scenario_id = record['scenario_id']
    screenshots_dir_path = os.path.join(script_dir, f"/output/{timestamp}/{scenario_id}/screenshots/".lstrip("/"))

    # Get all image files from the folder
    image_extensions = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
    images = [img for img in os.listdir(screenshots_dir_path) if img.lower().endswith(image_extensions)]
    images = sorted(images)

    if not images:
        print("No images found in the specified folder.")
        return

    # Create an HTML file to display the images
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image Gallery</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            img {
                margin: 10px;
                max-width: 300px;
                max-height: 300px;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <h1>Image Gallery</h1>
    """

    for image in images:
        image_path = os.path.join(screenshots_dir_path, image).replace("\\", "/")
        html_content += f'<img src="file:///{image_path}" alt="{image}">\n'

    html_content += """
    </body>
    </html>
    """

    # Write the HTML content to a temporary file
    output_file = os.path.join(screenshots_dir_path, "index.html")
    with open(output_file, "w") as file:
        file.write(html_content)
    return output_file

def generate_html(data, output_file="output.html"):
    """
    Generates an HTML file from JSON data.

    :param data: List of dictionaries containing the data to display in the table.
    :param output_file: Name of the HTML file to create.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Scenarios Summary</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
            }
            th {
                background-color: #f4f4f4;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f1f1f1;
            }
        </style>
    </head>
    <body>
        <h1>Test Scenarios Summary</h1>
        <table>
            <thead>
                <tr>
                    <th>Secnario ID</th>
                    <th>Description</th>
                    <th>Text Logs</th>
                    <th>Screenshots</th>
                    <th>Execution Result</th>
                </tr>
            </thead>

    """

    for record in data:
        screenshots_filepath = generate_html_for_screenshots(record)
        html_content += f"""
                <tr>
                    <td>{record['scenario_id']}</td>
                    <td>{record['scenario_description']}</td>
                    <td>
                      <a href={record['log_url']}>
                        View
                      </a>
                    </td>
                    <td>
                      <a href="file://{screenshots_filepath}">
                        View
                      </a>
                    </td>
                    <td>{record['execution_result']}</td>
                </tr>
        """

    html_content += """
            </tbody>
        </table>
    </body>
    </html>
    """

    # Write the generated HTML content to the output file
    with open(output_file, "w") as file:
        file.write(html_content)

    print(f"HTML file generated: {output_file}")
