from gdrive_func import authenticate_google_drive, upload_folder 
import json
from datetime import datetime

CONFIG_FILE = './drive_config.json'

def main():
    service = authenticate_google_drive()
    folder_path = "./my_model"
    new_folder_name = f'{datetime.now()}'
    folder_id = upload_folder(service, folder_path, new_folder_name=new_folder_name)
    print(f"Folder uploaded with ID: {folder_id}")
    with open(CONFIG_FILE, 'r') as file:
        data = json.load(file)
    
    data[new_folder_name] = folder_id

    with open(CONFIG_FILE, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == '__main__':
    main()
