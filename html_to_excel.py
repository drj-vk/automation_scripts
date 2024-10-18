import pandas as pd
from bs4 import BeautifulSoup

# Function to parse HTML content and extract relevant information
def extract_info_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Prepare lists to store the extracted data
    names = []
    websites = []
    categories = []
    instagrams = []

    # Find all the relevant 'article' elements in the HTML
    articles = soup.find_all('article', class_='_m-sm-bt')

    for article in articles:
        # Extract brand name, website, category, and Instagram
        brand_info = article.find('div', class_='both-about__txt cms-editor').find('p')
        
        # Extracting Name and Website
        if brand_info.find('a'):
            name = brand_info.find('a').text.strip()
            website = brand_info.find('a')['href'].strip()
        else:
            name = 'Not available'
            website = 'Not available'

        # Extracting Category
        category = brand_info.text.split('|')[1].strip() if '|' in brand_info.text else 'Not available'

        # Extracting Instagram
        if 'Instagram' in brand_info.text:
            instagram_tag = brand_info.find_all('a')[-1]
            instagram = instagram_tag['href'].strip() if 'instagram' in instagram_tag['href'] else 'Not available'
        else:
            instagram = 'Not available'

        # Append the data to the lists
        names.append(name)
        websites.append(website)
        categories.append(category)
        instagrams.append(instagram)

    return names, websites, categories, instagrams

# Read the HTML file
html_file = 'webpage_directory.txt'  # Replace with your HTML file path
with open(html_file, 'r', encoding='utf-8') as file:
    html_content = file.read()

# Extract the information from HTML
names, websites, categories, instagrams = extract_info_from_html(html_content)

# Create a DataFrame from the extracted data
df = pd.DataFrame({
    'Name': names,
    'Website': websites,
    'Category': categories,
    'Instagram': instagrams
})

# Save the DataFrame to an Excel file
output_file = 'output_brands.xlsx'
df.to_excel(output_file, index=False)

print(f"Data has been extracted and saved to {output_file}")
