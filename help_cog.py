import discord
from discord.ext import commands
import random
import asyncio
import logging
from datetime import datetime, timedelta
from data_manager import DataManager

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_manager = DataManager()

    @commands.command(name='help')
    async def helpz(self, ctx, category: str = None):
        help_details = {
            'Pet': {
                'hunt': (
                    "```"
                    "`!hunt`\n"
                    "Sử dụng lệnh này để bắt một thú cưng ngẫu nhiên từ danh sách các thú cưng có sẵn. Để tránh spam, có thời gian chờ 15 giây giữa các lần sử dụng lệnh này.\n"
                    "Tỷ lệ bắt được thú cưng phụ thuộc vào độ hiếm của chúng."
                    "```"
                ),
                'zoo': (
                    "```"
                    "`!zoo`\n"
                    "Xem danh sách tất cả các thú cưng mà bạn đã bắt được. Lệnh này sẽ không hiển thị thông tin chi tiết về cấp độ, tấn công và máu của từng thú cưng."
                    "```"
                ),
                'pet_info': (
                    "```"
                    "`!pet_info <pet>`\n"
                    "Xem thông tin chi tiết về pet của bạn. Bạn có thể thấy chỉ số về kinh nghiệm, tấn công, máu và phòng thủ của thú cưng."
                    "```"
                ),
                'sell': (
                    "```"
                    "`!sell <pet>`\n"
                    "Bán một thú cưng mà bạn đã bắt được để nhận tiền. Sau khi bán, thú cưng sẽ bị xóa khỏi danh sách của bạn."
                    "```"
                ),
                'upgrade': (
                    "```"
                    "`!upgrade <pet> <index>`\n"
                    "Nâng cấp một thú cưng trong danh sách của bạn. Bạn có thể nâng cấp cấp độ, tấn công và máu của thú cưng. Chi phí nâng cấp dựa trên cấp độ hiện tại của thú cưng."
                    "```"
                )
            },
            'Economy': {
                'balance': (
                    "```"
                    "`!balance`\n"
                    "Kiểm tra số tiền hiện có trong tài khoản của bạn."
                    "```"
                ),
                'daily': (
                    "```"
                    "`!daily`\n"
                    "Nhận phần thưởng hàng ngày. Phần thưởng sẽ được cung cấp mỗi 24 giờ, với giá trị phần thưởng là 100 đồng."
                    "```"
                ),
                'work': (
                    "```"
                    "`!work`\n"
                    "Đi làm để kiếm tiền. Lệnh này có thời gian chờ 10 phút giữa các lần sử dụng và bạn có thể kiếm từ 10 đến 50 đồng mỗi lần làm việc."
                    "```"
                ),
            },
            'Minigame': {
                'question': (
                    "```"
                    "`!question`\n"
                    "Tham gia vào trò chơi câu hỏi để trả lời các câu hỏi và kiếm điểm. Sau khi hoàn thành, bạn sẽ nhận được phần thưởng và có thể xem kết quả của mình."
                    "```"
                ),
            },
            'No Category': {
                'help': (
                    "```"
                    "`!help`\n"
                    "Hiển thị danh sách lệnh và chi tiết lệnh bằng `!help <category>`"
                    "```"
                ),
                'ping': (
                    "```"
                    "`!ping`\n"
                    "Pong"
                    "```"
                )
            }
        }

        if category is None:
            embed = discord.Embed(title="Danh sách các lệnh", color=0x00ff00)
            embed.description = (
                "**Pet Commands:**\n"
                "`!hunt` - Bắt thú cưng.\n"
                "`!zoo` - Xem danh sách thú cưng của bạn.\n"
                "`!pet_info <pet>` - Xem thông tin chi tiết thú cưng của bạn.\n"
                "`!sell <pet>` - Bán một thú cưng.\n"
                "`!upgrade <pet> <index>` - Nâng cấp thú cưng.\n"
                "\n**Economy Commands:**\n"
                "`!daily` - Nhận phần thưởng hàng ngày.\n"
                "`!work` - Kiếm tiền ngẫu nhiên bằng cách làm việc.\n"
                "`!balance` - Kiểm tra số dư của bạn.\n"
                "||`!add_money <@user>` - *Chỉ dành cho quản trị viên. Cộng thêm số dư của người chơi.*||\n"
                "||`!reset_money <@user>` - *Chỉ dành cho quản trị viên. Đưa số dư của người chơi về 0.*||\n"
                "\n**Minigame Commands:**\n"
                "`!question` - Tham gia trò chơi câu hỏi.\n"
                "\n**Khác:**\n"
                "`!ping` - Pong.\n"
                "`!help` - Hiển thị danh sách lệnh này.\n"
                "\n**Các lưu ý:**\n"
                "- Để biết thêm chi tiết về một lệnh cụ thể, hãy sử dụng `!help <category>`."
            )
            await ctx.send(embed=embed)
        else:
            category = category.capitalize()
            if category in help_details:
                embed = discord.Embed(title=f"Chi tiết lệnh trong mục `{category}`", color=0x00ff00)
                for command, description in help_details[category].items():
                    embed.add_field(name=f"`{command}`", value=description, inline=False)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="Danh mục không tồn tại", color=0xff0000)
                embed.description = (
                    f"Danh mục `{category}` không tồn tại. Sử dụng `!help` để xem danh sách các danh mục có sẵn."
                )
                await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
