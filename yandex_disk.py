def upload_to_yandex_disk(file_path, file_name):
    import yadisk
    YANDEX_TOKEN = "y0_AgAAAAAOr1PqAAz-1gAAAAEdJa4IAABXJb_jVLtA4KADEuELZCo4DSCFpQ"
    y = yadisk.YaDisk(token=YANDEX_TOKEN)
    
    y.upload(file_path, f"/{file_name}")
    return y.get_download_link(f"/{file_name}")
