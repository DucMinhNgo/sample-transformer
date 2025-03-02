from gdrive_func import authenticate_google_drive, download_folder 

def main():
    service = authenticate_google_drive()
    
    # Download thư mục từ Google Drive
    folder_id = "178b2NBqYvOk7Vv4outVTWhyQtD7Cpgav" 
    download_path = "dustin_model"
    download_folder(service, folder_id, download_path)
    print(f"Folder downloaded to: {download_path}")

if __name__ == '__main__':
    main()