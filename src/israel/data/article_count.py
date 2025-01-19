import json
# Specify the path to your JSON file
file_path = r'C:\Users\Admin\PycharmProjects\AI-Projects\News-Bias\news-bias-model\src\israel\data\article_urls.json'

# Open the file using a context manager (which ensures proper closing of the file)
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Now that 'data' contains the loaded JSON, you can work with it.
for key, value in data.items():
    # Print the key and the length of the list in value
    print(f"{key}: {len(value)}")