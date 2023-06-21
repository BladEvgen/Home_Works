import threading
import requests
import time
import tkinter as tk
import os

url = "https://picsum.photos/320/240/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) '
                  'Chrome/102.0.0.0 Safari/537.36'
}

local_path = os.path.join(os.path.dirname(__file__), "temp")

os.makedirs(local_path, exist_ok=True)

def execution_time(function):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = function(*args, **kwargs)
        print(f"Execution time: {time.perf_counter() - start_time} ")
        return result
    return wrapper

@execution_time
def sync_download_images():
    for i in range(10):
        response = requests.get(url, headers=headers)
        with open(os.path.join(local_path, f"image_sync_{i}.jpg"), "wb") as f:
            f.write(response.content)

@execution_time
def threaded_download_images():
    def download_image(index):
        response = requests.get(url, headers=headers)
        with open(os.path.join(local_path, f"image_thread_{index}.jpg"), "wb") as f:
            f.write(response.content)

    threads = []
    for i in range(10):
        thread = threading.Thread(target=download_image, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

root = tk.Tk()
root.geometry("500x200") 

sync_button = tk.Button(root, text="Sync Download", command=sync_download_images)
sync_button.pack()

threaded_button = tk.Button(root, text="Threaded Download", command=threaded_download_images)
threaded_button.pack()

root.mainloop()
