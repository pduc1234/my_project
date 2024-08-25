import discord
from discord.ext import commands
import random
import asyncio
import logging
from datetime import datetime, timedelta
from data_manager import DataManager

logging.basicConfig(level=logging.DEBUG)

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_manager = DataManager()
        self.rarity_map = {
            "common": "Thường",
            "uncommon": "Phổ Biến",
            "epic": "Hiếm",
            "rare": "Siêu Hiếm",
            "super": "Cực Hiếm",
            "ultra": "Sử Thi",
            "mythical": "Thần Thoại",
            "legendary": "Huyền Thoại"
        }

    async def log_debug(self, message):
        await self.data_manager.log_to_channel(self.bot, message)
        
    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.send('Pong!')

    # Economy Commands
    @commands.command(name='daily')
    async def daily(self, ctx):
        user_id = str(ctx.author.id)
        now = datetime.now()
        data = self.data_manager.data

        # Kiểm tra dữ liệu người dùng
        if user_id not in data:
            data[user_id] = {'pets': [], 'balance': 0, 'last_daily': None, 'last_work': None}
        user_data = data[user_id]

        last_daily = user_data.get('last_daily')

        if last_daily:
            last_daily = datetime.fromisoformat(last_daily)
            time_diff = now - last_daily
            if time_diff < timedelta(days=1):
                remaining_time = timedelta(days=1) - time_diff
                hours, remainder = divmod(remaining_time.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                await ctx.send(
                    f'Bạn đã nhận phần thưởng hàng ngày rồi. Vui lòng quay lại sau `{hours} giờ {minutes} phút`.'
                )
                return

        daily_reward = 100
        user_data['balance'] += daily_reward
        user_data['last_daily'] = now.isoformat()
        self.data_manager.data = data
        await self.log_debug(f'User {ctx.author.id} claimed daily reward.')
        await ctx.send(f'Bạn đã nhận được phần thưởng hàng ngày là **{daily_reward} :euro:**!')

    @commands.command(name='work')
    async def work(self, ctx):
        user_id = str(ctx.author.id)
        now = datetime.now()
        data = self.data_manager.data

        # Kiểm tra dữ liệu người dùng
        if user_id not in data:
            data[user_id] = {'pets': [], 'balance': 0, 'last_daily': None, 'last_work': None}
        user_data = data[user_id]
        last_work = user_data.get('last_work')

        if last_work:
            last_work = datetime.fromisoformat(last_work)
            time_diff = now - last_work

            if time_diff < timedelta(minutes=10):
                remaining_time = timedelta(minutes=10) - time_diff
                minutes = remaining_time.seconds // 60
                seconds = remaining_time.seconds % 60

                await ctx.send(
                    f'Đừng làm việc quá sức. Hãy quay lại sau khi nghỉ ngơi `{minutes} phút {seconds} giây`.'
                )
                return

        amount = random.randint(10, 50)
        user_data['balance'] += amount
        user_data['last_work'] = now.isoformat()
        self.data_manager.data = data
        await self.log_debug(f'User {ctx.author.id} worked and earned {amount} :euro:.')
        await ctx.send(f'Bạn đã nhận được phần thưởng là **{amount} :euro:**!')

    @commands.command(name='balance')
    async def balance(self, ctx):
        """Hiển thị số dư của người chơi."""
        user_id = str(ctx.author.id)
        data = self.data_manager.data

        # Kiểm tra dữ liệu người dùng
        if user_id not in data:
            data[user_id] = {'pets': {}, 'balance': 0}

        balance = data[user_id].get("balance", 0)
        await ctx.send(f"Số dư hiện tại của bạn là **{int(balance)} :euro:**.")

    @commands.command(name='reset_money')
    @commands.has_permissions(administrator=True)
    async def reset_money(self, ctx):
        user_id = str(ctx.author.id)
        data = self.data_manager.data

        # Kiểm tra dữ liệu người dùng
        if user_id not in data:
            data[user_id] = {'pets': [], 'balance': 0, 'last_daily': None, 'last_work': None}
        data[user_id]["balance"] = 0
        self.data_manager.data = data
        await ctx.send("Số tiền của bạn đã được trừ hết!")

    @commands.command(name='add_money')
    @commands.has_permissions(administrator=True)
    async def add_money(self, ctx, user: discord.User = None, amount: int = None):
        data = self.data_manager.data
        if user is None or amount is None:
            await ctx.send("Bạn cần chỉ định người dùng và số tiền.")
            return

        user_id = str(user.id)
        # Kiểm tra dữ liệu người dùng
        if user_id not in data:
            data[user_id] = {'pets': [], 'balance': 0, 'last_daily': None, 'last_work': None}

        if amount <= 0:
            await ctx.send("Số tiền phải lớn hơn 0.")
            return

        data[user_id]["balance"] += amount
        self.data_manager.data = data
        await ctx.send(f"Đã thêm **{amount} :euro:** vào tài khoản của người dùng `{user}`.")

    # Pet Commands
    @commands.command(name='hunt')
    async def catch_pet(self, ctx):
        user_id = str(ctx.author.id)
        data = self.data_manager.data
        pets = self.data_manager.pets_data

        if user_id not in data:
            data[user_id] = {"pets": {}, "balance": 0, "last_hunt": None}

        user_data = data[user_id]
        last_hunt_time = user_data.get("last_hunt")
        COOLDOWN_TIME = 15  # 15 giây

        if last_hunt_time:
            try:
                last_hunt_time = datetime.strptime(last_hunt_time,
                                                   "%Y-%m-%d %H:%M:%S")
            except ValueError:
                last_hunt_time = None

            cooldown_remaining = (datetime.utcnow() - last_hunt_time).total_seconds()

            if cooldown_remaining < COOLDOWN_TIME:
                time_remaining = int(COOLDOWN_TIME - cooldown_remaining)
                message = await ctx.send(
                    f"Bạn cần chờ thêm `{time_remaining} giây` nữa để có thể bắt thú cưng!"
                )

                while time_remaining > 0:
                    await asyncio.sleep(1)
                    time_remaining -= 1
                    await message.edit(
                        content=
                        f"Bạn cần chờ thêm `{time_remaining} giây` nữa để có thể bắt thú cưng!"
                    )

                await message.delete()
                return

        # Debugging: Check if pets data is loaded correctly
        if not pets:
            await ctx.send("Không có dữ liệu thú cưng nào được tải.")
            return

        pet_items = list(pets.items())
        if not pet_items:
            await ctx.send("Không có thú cưng nào để bắt.")
            return

        # Debugging: Print pet items and weights
        weights = [pet_info["catch_rate"] for _, pet_info in pet_items]
        if not weights or len(weights) != len(pet_items):
            await ctx.send("Có lỗi xảy ra khi lấy dữ liệu thú cưng.")
            print("Pet items:", pet_items)
            print("Weights:", weights)
            return

        # Tiến hành bắt thú cưng
        pet, pet_data = random.choices(pet_items, weights=weights, k=1)[0]

        # Tìm ra rarity và thông tin của pet
        rarity = pet_data["rarity"]
        rarity_label = self.rarity_map.get(rarity, rarity)

        if pet not in user_data["pets"]:
            user_data["pets"][pet] = []

        user_data["pets"][pet].append({
            "level": pet_data["level"],
            "attack": pet_data["attack"],
            "health": pet_data["health"],
            "defense": pet_data["defense"],
            "exp": 0
        })

        user_data["last_hunt"] = datetime.utcnow().strftime(
            "%Y-%m-%d %H:%M:%S")
        self.data_manager.data = data

        embed = discord.Embed(title="Chúc Mừng!",
                              description=f"Bạn đã bắt được một **`{pet}`**!",
                              color=discord.Color.green())
        embed.add_field(name="Độ Hiếm", value=rarity_label, inline=True)
        embed.add_field(name="Tấn Công", value=pet_data["attack"], inline=True)
        embed.add_field(name="Máu", value=pet_data["health"], inline=True)
        embed.add_field(name="Phòng Thủ",
                        value=pet_data["defense"],
                        inline=True)
    
        await ctx.send(embed=embed)
        await self.log_debug(f'User {ctx.author.id} initiated a hunt.')
        
    @commands.command(name='sell')
    async def sell_pet(self, ctx, pet: str, quantity: int = 1):
        user_id = str(ctx.author.id)
        data = self.data_manager.data

        # Khởi tạo dữ liệu người dùng nếu chưa tồn tại
        if user_id not in data:
            data[user_id] = {'pets': {}, 'balance': 0}

        user_data = data[user_id]
        pet_names = self.data_manager.pet_names

        # Kiểm tra tên thú cưng và tìm emoji tương ứng
        pet_emoji = next(
            (emoji for emoji, name in pet_names.items() if name == pet), None)

        if pet_emoji is None:
            await ctx.send(f'Tên thú cưng `{pet_emoji}` không hợp lệ!')
            return

        # Kiểm tra xem người dùng có sở hữu đủ số lượng thú cưng này không
        if pet_emoji not in user_data.get('pets', {}):
            await ctx.send(f'Bạn không sở hữu thú cưng `{pet}`!')
            return

        pet_list = user_data['pets'][pet_emoji]
        pet_count = len(pet_list)

        if pet_count < quantity:
            await ctx.send(
                f'Bạn không sở hữu đủ số lượng thú cưng `{pet}` để bán!')
            return

        # Xác định giá của pet
        pets_data = self.data_manager.pets_data
        if pet_emoji not in pets_data:
            await ctx.send("Thông tin pet không tồn tại.")
            return

        pet_value = pets_data[pet_emoji].get('price', 0)
        total_value = pet_value * quantity

        # Cập nhật số dư và xóa pet
        user_data['balance'] += total_value

        # Xóa số lượng pet cần bán
        user_data['pets'][pet_emoji] = pet_list[quantity:]

        # Lưu dữ liệu
        self.data_manager.data = data
        self.data_manager.save_json('data.json', self.data_manager.data)

        # Debugging
        await self.log_debug(f'User {ctx.author.id} sold {quantity} {pet}. Total value: {total_value}.')
        await ctx.send(f'Bạn đã bán {quantity} `{pet_emoji}` với tổng giá **{total_value}** :euro:.')

    @commands.command(name='upgrade')
    async def upgrade_pet(self, ctx, pet: str, index=None):
        user_id = str(ctx.author.id)
        data = self.data_manager.data
        pet_names = self.data_manager.pet_names
        pets_data = self.data_manager.pets_data

        # Tìm emoji của thú cưng từ tên văn bản
        pet_emoji = next(
            (emoji for emoji, name in pet_names.items() if name == pet), None)

        if pet_emoji is None or user_id not in data or pet_emoji not in data[
                user_id]["pets"]:
            await ctx.send('Bạn không sở hữu thú cưng này!')
            return

        pets_list = data[user_id]["pets"][pet_emoji]

        # Nếu không có chỉ số, tìm thú cưng có level cao nhất để nâng cấp
        if index is None:
            index = max(range(len(pets_list)),
                        key=lambda i: pets_list[i]["level"])

        if index < 0 or index >= len(pets_list):
            await ctx.send('Chỉ số thú cưng không hợp lệ!')
            return

        pet_info = pets_list[index]
        current_exp = pet_info.get("exp", 0)
        current_level = pet_info["level"]
        exp_needed = pets_data[pet_emoji]["exp_needed"]
        exp_needed_for_upgrade = current_level * 1.5 * exp_needed

        max_upgrade_exp = min(10, exp_needed_for_upgrade - current_exp)
        upgrade_cost = current_level * 0.5 * 50

        # Logic tính điểm exp và chỉ số
        if data[user_id]["balance"] >= upgrade_cost:
            data[user_id]["balance"] -= upgrade_cost
            pet_info["exp"] += max_upgrade_exp
            if pet_info["exp"] >= exp_needed_for_upgrade:
                pet_info["exp"] = exp_needed_for_upgrade
                pet_info["level"] += 1
                pet_info["attack"] += 2.5
                pet_info["health"] += 15

                # Cứ mỗi 5 cấp độ, tăng 1 điểm phòng thủ
                if pet_info["level"] % 5 == 0:
                    pet_info["defense"] += 1

            self.data_manager.data = data

            exp_percentage = (pet_info["exp"] / exp_needed_for_upgrade) * 100

            await ctx.send(
                f'Bạn đã tăng **{max_upgrade_exp}** điểm kinh nghiệm cho `{pet_emoji}` (Vị trí số {index}).\n'
                f'**Kinh nghiệm hiện tại**: {int(exp_percentage)}%\n'
                f'**Chi phí nâng cấp**: {int(upgrade_cost)} :euro:.')
        else:
            await ctx.send(f'Bạn không có đủ tiền để nâng cấp thú cưng `{pet_emoji}` lên level tiếp theo!') 
        await self.log_debug(f'User {ctx.author.id} upgraded pet `{pet}` (Index: {index}).')

    @commands.command(name='zoo')
    async def zoo(self, ctx):
        user_id = str(ctx.author.id)
        data = self.data_manager.data
        pet_data = self.data_manager.pets_data

        # Kiểm tra xem người dùng có thú cưng không
        if user_id not in data or not data[user_id]["pets"]:
            await ctx.send('Bạn chưa có thú cưng nào!')
            return

        user_pets = data[user_id]["pets"]

        # Tạo danh sách các loại thú cưng với độ hiếm
        pets_by_rarity = {}
        for pet, pets_list in user_pets.items():
            # Lấy thông tin độ hiếm từ pet_data
            pet_info = pet_data.get(pet, {})
            pet_rarity = pet_info.get("rarity", "Không xác định")
            # Chuyển đổi độ hiếm thành nhãn sử dụng rarity_map
            rarity_label = self.rarity_map.get(pet_rarity, pet_rarity)

            if rarity_label not in pets_by_rarity:
                pets_by_rarity[rarity_label] = {}
            if pet not in pets_by_rarity[rarity_label]:
                pets_by_rarity[rarity_label][pet] = 0
            pets_by_rarity[rarity_label][pet] += len(pets_list)

        # Sắp xếp độ hiếm theo thứ tự
        rarity_order = {
            "Thường": 1,
            "Phổ Biến": 2,
            "Hiếm": 3,
            "Siêu Hiếm": 4,
            "Cực Hiếm": 5,
            "Sử Thi": 6,
            "Thần Thoại": 7,
            "Huyền Thoại": 8
        }
        sorted_rarities = sorted(pets_by_rarity.keys(),
                                 key=lambda r: rarity_order.get(r, 0),
                                 reverse=True)

        # Tạo embed để hiển thị
        embed = discord.Embed(title="🌟 **Thú cưng của bạn** 🌟",
                              color=discord.Color.blue())

        for rarity in sorted_rarities:
            pets_list = pets_by_rarity[rarity]
            pets_display = " | ".join(f"`{pet}` {count}"
                                      for pet, count in pets_list.items())
            embed.add_field(name=rarity, value=pets_display, inline=False)

        await ctx.send(embed=embed)
        await self.log_debug(f'User {ctx.author.id} viewed their zoo.')

    @commands.command(name='pet_info')
    async def pet_info(self, ctx, pet: str, index: int = None):
        user_id = str(ctx.author.id)
        data = self.data_manager.data
        pet_data = self.data_manager.pets_data
        pet_names = self.data_manager.pet_names

        # Kiểm tra tên thú cưng và tìm emoji tương ứng
        pet_emoji = next(
            (emoji for emoji, name in pet_names.items() if name == pet), None)

        if pet_emoji is None:
            await ctx.send(f'Tên thú cưng `{pet}` không hợp lệ!')
            return

        # Kiểm tra xem người dùng có sở hữu thú cưng này không
        user_data = data.get(user_id, {})
        if pet_emoji not in user_data.get('pets', {}):
            await ctx.send(f'Bạn không sở hữu thú cưng `{pet}`!')
            return

        pets_list = user_data['pets'][pet_emoji]

        # Nếu không có chỉ số, tìm thú cưng có level cao
        if index is None:
            pets_list = sorted(pets_list, key=lambda x: x["level"], reverse=True)[:3]
        else:
            if index < 0 or index >= len(pets_list):
                await ctx.send('Chỉ số thú cưng không hợp lệ!')
                return
            pets_list = [pets_list[index]]

        for i, pet_info in enumerate(pets_list):
            current_exp = pet_info.get("exp", 0)
            current_level = pet_info["level"]
            exp_needed = pet_data.get(pet_emoji, {}).get("exp_needed", 1)
            exp_needed_for_upgrade = current_level * 1.5 * exp_needed
            exp_percentage = int((current_exp / exp_needed_for_upgrade) * 100) if exp_needed_for_upgrade else 0

            pet_name = pet_names.get(pet_emoji, "Unknown Pet")

            embed = discord.Embed(title=f"Thông Tin Chi Tiết của `{pet_emoji}` ({pet_name})", color=discord.Color.blue())
            embed.add_field(name="Vị trí", value=f"Vị trí số {index if index is not None else i}", inline=False)
            embed.add_field(name="Level & Kinh Nghiệm", value=f"Level: {pet_info['level']} | Kinh Nghiệm: {int(current_exp)}/{int(exp_needed_for_upgrade)} ({exp_percentage}%)", inline=True)
            embed.add_field(name="Tấn Công, Máu & Phòng Thủ", value=f":crossed_swords: {pet_info.get('attack', 'Chưa có thông tin')} | :drop_of_blood: {pet_info.get('health', 'Chưa có thông tin')} | :shield: {pet_info.get('defense', 'Chưa có thông tin')}", inline=True)

            await ctx.send(embed=embed)

    # Minigame Commands
    @commands.command(name='question')
    async def question(self, ctx):
        """Lệnh để hỏi các câu hỏi ngẫu nhiên."""
        data = self.data_manager.data
        questions = self.data_manager.questions

        await ctx.send("Vui lòng chọn độ khó: easy, medium, hoặc hard.")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["easy", "medium", "hard"]

        try:
            difficulty_msg = await self.bot.wait_for("message", check=check, timeout=30)
            difficulty = difficulty_msg.content.lower()
        except asyncio.TimeoutError:
            await ctx.send("Bạn đã không chọn độ khó trong thời gian quy định.")
            return

        # Lấy tất cả câu hỏi của độ khó đã chọn
        all_questions = []
        for topic, levels in questions.items():
            if difficulty in levels:
                all_questions.extend(levels[difficulty])

        if not all_questions:
            await ctx.send(f"Không tìm thấy câu hỏi cho độ khó {difficulty}.")
            return

        # Chọn ngẫu nhiên tối đa 40 câu hỏi
        selected_questions = random.sample(all_questions, min(3, len(all_questions)))

        # Theo dõi điểm số và câu trả lời
        correct_answers = 0
        incorrect_answers = 0
        wrong_questions = []

        for question_data in selected_questions:
            question_text = question_data['question']
            options = question_data['options']
            correct_answer = question_data['answer']

            # Tạo embed cho câu hỏi
            embed = discord.Embed(title="Câu hỏi", description=question_text)
            for idx, option in enumerate(options, 1):
                embed.add_field(name=f"Option {idx}", value=option, inline=False)

            await ctx.send(embed=embed)

            # Chờ người chơi trả lời
            def answer_check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

            try:
                msg = await self.bot.wait_for('message', check=answer_check, timeout=30.0)
                user_answer_index = int(msg.content) - 1

                if 0 <= user_answer_index < len(options):
                    user_answer = options[user_answer_index]
                    if user_answer == correct_answer:
                        correct_answers += 1
                    else:
                        incorrect_answers += 1
                        wrong_questions.append((question_text, correct_answer, user_answer))
                else:
                    await ctx.send("Đáp án không hợp lệ. Đánh dấu là sai.")
                    incorrect_answers += 1
                    wrong_questions.append((question_text, correct_answer, "Không hợp lệ"))

            except asyncio.TimeoutError:
                await ctx.send("Hết thời gian chờ! Không có câu trả lời nào được đưa ra.")
                incorrect_answers += 1
                wrong_questions.append((question_text, correct_answer, "Không trả lời"))

        # Tạo embed tổng kết
        summary_embed = discord.Embed(title="Kết quả", description="Dưới đây là kết quả bài kiểm tra của bạn:")
        summary_embed.add_field(name="Số câu hỏi", value=len(selected_questions), inline=False)
        summary_embed.add_field(name="Số câu đúng", value=correct_answers, inline=False)
        summary_embed.add_field(name="Số câu sai", value=incorrect_answers, inline=False)

        if wrong_questions:
            wrong_details = "\n".join([f"Câu hỏi: {q[0]}\nĐáp án đúng: {q[1]}\nĐáp án của bạn: {q[2]}\n" for q in wrong_questions])
            summary_embed.add_field(name="Chi tiết câu trả lời sai", value=wrong_details, inline=False)
        else:
            summary_embed.add_field(name="Chi tiết câu trả lời sai", value="Không có câu trả lời sai.", inline=False)

        # Tính tỷ lệ câu trả lời đúng
        total_questions = len(selected_questions)
        accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

        # Tạo embed phần thưởng
        reward_embed = discord.Embed(title="Kết quả bài kiểm tra", description=f"Người chơi: `{ctx.author.name}`")
        reward_embed.add_field(name="Tỷ lệ đúng", value=f"{accuracy:.2f}%", inline=False)

        if accuracy > 60:
            user_id = str(ctx.author.id)

            def update_user_data(user_data):
                if "balance" not in user_data:
                    user_data["balance"] = 0

                user_data["balance"] += 10
                return True

            self.data_manager.update_data(user_id, update_user_data)
            reward_embed.add_field(name="Phần thưởng",
                                   value="Chúc mừng! Bạn đã nhận được **10** :euro:.",
                                   inline=False)
        else:
            reward_embed.add_field(name="Phần thưởng",
                                   value=f"Rất tiếc! Không có phần quà nào dành cho bạn. Hãy cố gắng trong lần tới nhé!",
                                   inline=False)

        await ctx.send(embed=summary_embed)
        await ctx.send(embed=reward_embed)

async def setup(bot):
    await bot.add_cog(Commands(bot))
