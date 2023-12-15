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


import requests
from bs4 import BeautifulSoup
import csv
import json

# Function to process each video link
def process_video_link(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Initialize the data dictionary with default values
    data = {
        'link': link,
        'Views': 'Not Found',
        'Likes': 'Not found',
        'Shares': 'Not found',
        'Saves': 'Not found',
        'Comments': 'Not found',
    }

 # Attempt to find each piece of data and update the dictionary if found
    likes_element = soup.find('strong', attrs={'data-e2e': 'like-count'})
    if likes_element:
        data['Likes'] = likes_element.get_text()

    comments_element = soup.find('strong', attrs={'data-e2e': 'comment-count'})
    if comments_element:
        data['Comments'] = comments_element.get_text()

    saves_element = soup.find('strong', attrs={'data-e2e': 'undefined-count'})  # Update with correct identifier
    if saves_element:
        data['Saves'] = saves_element.get_text()

    shares_element = soup.find('strong', attrs={'data-e2e': 'share-count'})  # Update with correct identifier
    if shares_element:
        data['Shares'] = shares_element.get_text()

    play_count_element = soup.find('strong', attrs={'data-e2e': 'play-count'})  # Update with correct identifier
    if play_count_element:
        data['Play_Count'] = play_count_element.get_text()

    return data

# Main function to iterate over links and write data to CSV
def scrape_tiktok_videos():
    csv_columns = ['link', 'Views', 'Likes', 'Shares', 'Saves', 'Comments']
    with open('Video_Data.csv', 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()

        with open('VideoLinks.txt', 'r') as file:
            filedata = [v.strip() for v in file.read().split('\n')]

        for link in filedata:
            item = process_video_link(link)
            writer.writerow(item)

# Run the script
if __name__ == '__main__':
    scrape_tiktok_videos()

