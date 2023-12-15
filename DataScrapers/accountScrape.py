import requests
from bs4 import BeautifulSoup
import csv
import os

# Function to convert styled numbers to float
def style_num_to_float(style_num):
    if 'K' in style_num:
        return float(style_num.replace('K', '')) * 1000
    elif 'M' in style_num:
        return float(style_num.replace('M', '')) * 1000000
    else:
        return float(style_num)
    
# Function to fetch data from a TikTok link
def fetch_tiktok_data(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all elements with 'data-e2e="video-views"'
    video_views_elements = soup.find_all('strong', attrs={'data-e2e': 'video-views'})

    # Extract views from the first three videos, convert them to float
    video_views = [style_num_to_float(element.get_text()) for element in video_views_elements[:3]]

    item = {
        'Influencer': link.replace('https://www.tiktok.com/@', ''),
        'link': link,
        'video 1': video_views[0] if len(video_views) > 0 else None,
        'video 2': video_views[1] if len(video_views) > 1 else None,
        'video 3': video_views[2] if len(video_views) > 2 else None,
        # Placeholder for other data fields (e.g., Follower count, Following count, etc.)
        'Average Views': sum(video_views) / len(video_views) if video_views else None,
        'Multiplier': ''  # Placeholder for any additional calculations or data
    }
    
    return item

# Main function to process data
def get_data():
    print("Current Working Directory: ", os.getcwd())

    csv_columns = ['Influencer', 'link', 'Follower count', 'Following count', 'Like count', 'video 1', 'video 2', 'video 3', 'Average Views', 'Multiplier']
    csvfile = open('Account_Data.csv', 'w', newline='', encoding="utf-8")
    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
    writer.writeheader()

    input_file = open('AccountLinks.txt', 'r')
    file_data = input_file.read().split('\n')

    for link in file_data:
        try:
            item = fetch_tiktok_data(link)
            writer.writerow(item)
        except Exception as e:
            print(f'Error processing account {link}: {e}')

    csvfile.close()
    print("Thank you!")

# Run the script
if __name__ == '__main__':
    get_data()
