import os
import threading
import requests
import tkinter as tk
from multiprocessing import Pool
import asyncio
import aiohttp
import time

url = "https://picsum.photos/320/240/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) "
    "Chrome/102.0.0.0 Safari/537.36"
}

local_path = os.path.join(os.path.dirname(__file__), "temp")
os.makedirs(local_path, exist_ok=True)


def execution_time(function):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = function(*args, **kwargs)
        execution_time = time.perf_counter() - start_time
        print(f"Execution time: {execution_time:.7f} seconds")
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


@execution_time
async def async_download_images():
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for i in range(10):
            task = asyncio.create_task(download_image(session, i))
            tasks.append(task)

        await asyncio.gather(*tasks)


async def download_image(session, index):
    async with session.get(url) as response:
        with open(os.path.join(local_path, f"image_async_{index}.jpg"), "wb") as f:
            while True:
                chunk = await response.content.read(1024)
                if not chunk:
                    break
                f.write(chunk)


def download_image_multiprocess(index):
    response = requests.get(url=url, headers=headers)
    filename = f"image_multiprocess_{index}.jpg"
    file_path = os.path.join(local_path, filename)
    with open(file_path, "wb") as file:
        file.write(response.content)


@execution_time
def download_images_multiprocess():
    with Pool(processes=10) as pool:
        pool.map(download_image_multiprocess, range(10))


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("500x250")

    sync_button = tk.Button(
        root,
        text="Sync Download",
        command=sync_download_images,
        font=("Arial Bold", 20),
    )
    sync_button.pack()

    threaded_button = tk.Button(
        root,
        text="Threaded Download",
        command=threaded_download_images,
        font=("Arial Bold", 20),
    )
    threaded_button.pack()

    async_button = tk.Button(
        root,
        text="Async Download",
        command=lambda: asyncio.run(async_download_images()),
        font=("Arial Bold", 20),
    )
    async_button.pack()

    multiprocess_button = tk.Button(
        root,
        text="Multiprocess Download",
        command=download_images_multiprocess,
        font=("Arial Bold", 20),
    )
    multiprocess_button.pack()

    root.mainloop()
