import json
import os
from config import channel
from pathlib import Path
import logging

DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)
CHANNEL_ID = channel

class DataManager:
    def __init__(self):
        try:
            self._pets_data = self.load_json('pets.json')
            self._weapons_data = self.load_json('weapons.json')
            self._pet_names = self.load_json('pet_names.json')
            self._data = self.load_json('data.json')
            self._weapon_emojis = self.load_json('weapon_emojis.json')
            self._questions = self.load_json('deutsch_quest.json')
            self.channel_id = (CHANNEL_ID)
            print("DataManager khởi tạo thành công.")
        except Exception as e:
            print(f"Lỗi khi khởi tạo DataManager: {e}")

    async def log_to_channel(self, bot, message):
        channel = bot.get_channel(int(self.channel_id))
        if channel:
            await channel.send(message)
        else:
            print(f"Channel with ID {self.channel_id} not found.")

    def load_json(self, filename):
        """Tải dữ liệu từ tệp JSON và xử lý lỗi."""
        file_path = DATA_DIR / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"File không tồn tại: {file_path}")
            return {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(f"Lỗi khi đọc file JSON: {filename}. Dữ liệu không hợp lệ hoặc không thể giải mã.")
            self.backup_file(file_path)  # Sử dụng phương thức backup_file
            return {}

    def save_json(self, filename, data):
        """Lưu dữ liệu vào tệp JSON."""
        file_path = DATA_DIR / filename
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Lỗi khi ghi file JSON: {file_path}. Lỗi: {e}")
        except Exception as e:
            print(f"Lỗi không xác định khi ghi file JSON: {file_path}. Lỗi: {e}")

    def backup_file(self, file_path):
        """Sao lưu tệp JSON khi có lỗi."""
        backup_path = file_path.with_suffix('.backup.json')
        file_path.rename(backup_path)
        print(f"Đã sao lưu tệp lỗi: {file_path} -> {backup_path}")

    @property
    def questions(self):
        """Trả về dữ liệu câu hỏi."""
        return self._questions

    def get_questions(self):
        """Trả về dữ liệu câu hỏi như một phương thức."""
        return self._questions

    @property
    def pets_data(self):
        return self._pets_data

    @pets_data.setter
    def pets_data(self, value):
        self._pets_data = value
        self.save_json('pets.json', self._pets_data)

    @property
    def weapons_data(self):
        return self._weapons_data

    @weapons_data.setter
    def weapons_data(self, value):
        self._weapons_data = value
        self.save_json('weapons.json', self._weapons_data)

    @property
    def pet_names(self):
        return self._pet_names

    @property
    def weapon_emojis(self):
        return self._weapon_emojis

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self.save_json('data.json', self._data)

    def update_data(self, user_id, update_function):
        """Cập nhật dữ liệu của người dùng và lưu lại."""
        if user_id not in self._data:
            self._data[user_id] = {"pets": {}, "balance": 0}
        update_function(self._data[user_id])
        self.save_json('data.json', self._data)

    def add_pet(self, pet_name, pet_info):
        """Thêm một pet mới và lưu lại."""
        if pet_name not in self._pets_data:
            self._pets_data[pet_name] = pet_info
            self.save_json('pets.json', self._pets_data)

    def remove_pet(self, pet_name):
        """Xóa một pet và lưu lại."""
        if pet_name in self._pets_data:
            del self._pets_data[pet_name]
            self.save_json('pets.json', self._pets_data)

    def update_pet(self, pet_name, new_info):
        """Cập nhật thông tin pet và lưu lại."""
        if pet_name in self._pets_data:
            self._pets_data[pet_name].update(new_info)
            self.save_json('pets.json', self._pets_data)

