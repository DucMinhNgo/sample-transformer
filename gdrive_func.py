import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from io import BytesIO
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Phạm vi quyền (scope) để truy cập Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_google_drive():
    """Xác thực và trả về dịch vụ Google Drive."""
    creds = None
    # Kiểm tra file token.pickle để tải thông tin xác thực đã lưu
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Nếu không có thông tin xác thực hợp lệ, yêu cầu người dùng đăng nhập
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Lưu thông tin xác thực cho lần sau
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    # Trả về dịch vụ Google Drive
    return build('drive', 'v3', credentials=creds)

def create_folder(service, folder_name, parent_folder_id=None):
    """Tạo một thư mục trên Google Drive."""
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    if parent_folder_id:
        folder_metadata['parents'] = [parent_folder_id]
    
    folder = service.files().create(body=folder_metadata, fields='id').execute()
    return folder.get('id')

def find_folder_by_name(service, folder_name, parent_folder_id=None):
    """Tìm thư mục bằng tên và ID thư mục cha."""
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent_folder_id:
        query += f" and '{parent_folder_id}' in parents"
    
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])
    return folders[0]['id'] if folders else None

def upload_folder(service, folder_path, parent_folder_id=None, new_folder_name=None):
    """Upload một thư mục lên Google Drive, đổi tên thư mục gốc và giữ nguyên cấu trúc."""
    # Sử dụng tên mới cho thư mục gốc nếu được chỉ định
    folder_name = new_folder_name if new_folder_name else os.path.basename(folder_path)
    
    # Tạo thư mục gốc trên Google Drive với tên mới
    folder_id = create_folder(service, folder_name, parent_folder_id)
    print(f"Created folder: {folder_name} (ID: {folder_id})")
    
    # Duyệt qua tất cả các file và thư mục con
    for root, dirs, files in os.walk(folder_path):
        for dir_name in dirs:
            # Tạo thư mục con trên Google Drive
            dir_path = os.path.join(root, dir_name)
            relative_path = os.path.relpath(dir_path, folder_path)
            parent_id = folder_id
            
            # Tạo các thư mục con theo cấu trúc
            for part in relative_path.split(os.sep):
                # Kiểm tra xem thư mục con đã tồn tại chưa
                existing_folder_id = find_folder_by_name(service, part, parent_id)
                if existing_folder_id:
                    parent_id = existing_folder_id
                else:
                    parent_id = create_folder(service, part, parent_id)
        
        for file_name in files:
            # Upload file vào thư mục tương ứng
            file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(file_path, folder_path)
            parent_id = folder_id
            
            # Tìm thư mục cha dựa trên cấu trúc
            for part in os.path.dirname(relative_path).split(os.sep):
                if part:
                    # Kiểm tra xem thư mục con đã tồn tại chưa
                    existing_folder_id = find_folder_by_name(service, part, parent_id)
                    if existing_folder_id:
                        parent_id = existing_folder_id
                    else:
                        parent_id = create_folder(service, part, parent_id)
            
            # Upload file
            file_metadata = {
                'name': file_name,
                'parents': [parent_id],
            }
            media = MediaFileUpload(file_path, resumable=True)
            file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"Uploaded file: {file_name} (ID: {file.get('id')})")
    
    return folder_id

def download_folder(service, folder_id, download_path):
    """Download một thư mục từ Google Drive."""
    # Lấy danh sách các file trong thư mục
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name, mimeType)"
    ).execute()
    items = results.get('files', [])
    
    # Tạo thư mục đích nếu chưa tồn tại
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    
    # Download từng file
    for item in items:
        file_id = item['id']
        file_name = item['name']
        file_path = os.path.join(download_path, file_name)
        
        if item['mimeType'] == 'application/vnd.google-apps.folder':
            # Nếu là thư mục, đệ quy download
            download_folder(service, file_id, file_path)
        else:
            # Nếu là file, download file
            request = service.files().get_media(fileId=file_id)
            fh = BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Downloaded {file_name}: {int(status.progress() * 100)}%")
            
            # Lưu file
            with open(file_path, 'wb') as f:
                f.write(fh.getvalue())
            print(f"Saved file: {file_name}")