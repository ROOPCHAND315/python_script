import pandas as pd
import requests
import os
import mimetypes
import zipfile

def download_image(url, folder_path, filename):
    response = requests.get(url)
    if response.status_code == 200:
        content_type = response.headers.get('content-type')
        extension = mimetypes.guess_extension(content_type)
        if not extension:
            extension = '.jpg'
        filename_with_extension = filename + extension
        with open(os.path.join(folder_path, filename_with_extension), 'wb') as f:
            f.write(response.content)
        print(f"Image downloaded: {filename}")
    else:
        print(f"Failed to download image: {filename}")

def download_images_from_excel(excel_file, folder_path):
    df = pd.read_excel(excel_file)
    for index, row in df.iterrows():
        url = row['Image_URL']
        filename = row['Name']
        download_image(url, folder_path, filename)

def zip_folder(folder_path):
    if os.path.exists(folder_path+'.zip'):
        os.remove(folder_path+'.zip')

    with zipfile.ZipFile(folder_path+'.zip', 'w') as zip_object:
        for folder_name, sub_folders, file_names in os.walk(folder_path):
            for filename in file_names:
                file_path = os.path.join(folder_name, filename)
                zip_object.write(file_path, os.path.basename(file_path))

def main():
    excel_file = '/home/roopchand/test/scrapyTest/feedFinder/feedFinder/scripts/sheets/collect_data_sheet.xlsx'
    folder_path = '/home/roopchand/scrapytut/domain_icon'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    download_images_from_excel(excel_file, folder_path)

    zip_folder(folder_path)

if __name__ == "__main__":
    main()