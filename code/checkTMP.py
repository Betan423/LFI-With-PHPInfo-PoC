import os

def monitor_directory(directory_path):
    # 記錄目前目錄中的檔案
    seen_files = set(os.listdir(directory_path))
    while True:
        current_files = set(os.listdir(directory_path))
        
        # 比對目前目錄中的檔案與之前的檔案清單，找出新增的檔案
        new_files = current_files - seen_files
        
        if new_files:
            for new_file in new_files:
                file_path = os.path.join(directory_path, new_file)
                
                # 檢查檔案是否為檔案而非目錄
                if os.path.isfile(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                        print(f"New file added: {new_file}")
                        print("Content:")
                        print(content)
        
        # 更新已經看到的檔案清單
        seen_files = current_files

# 替換為你要監控的目錄路徑
directory_path = "C:\\Users\\betan\\AppData\\Local\\Temp"

print("開始監控是否有新的暫存檔")
monitor_directory(directory_path)
