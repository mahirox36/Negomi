from modules.Nexon import *

class MainPanel(View):
    def __init__(self, user: Member | User):
        super().__init__(timeout=900)
        self.user = user
        self.userData = UserData(user)

    @button(label="User Information", style=ButtonStyle.blurple)
    async def user_info(self, button: Button, interaction: Interaction):
        view = UserInfoPanel(self.user)
        await interaction.response.edit_message(embed=view.create_info_embed(), view=view)

    @button(label="Statistics", style=ButtonStyle.green)
    async def statistics(self, button: Button, interaction: Interaction):
        embed = Embed(title="User Statistics", color=colors.Info.value)
        data = self.userData.user_data
        embed.add_field(name="Messages", value=f"Total: `{data.total_messages}`\nEdited: `{data.edited_messages}`\nDeleted: `{data.deleted_messages}`")
        embed.add_field(name="Content", value=f"Characters: `{data.character_count}`\nWords: `{data.word_count}`")
        embed.add_field(name="Interactions", value=f"Mentions: `{data.mentions_count}`\nReplies: `{data.replies_count}`")
        embed.add_field(name="Reactions", value=f"Given: `{data.reactions_given}`\nReceived: `{data.reactions_received}`")
        embed.add_field(name="Commands Used", value=f"`{data.commands_used}`")
        
        view = BackPanel(self.user)
        await interaction.response.edit_message(embed=embed, view=view)

    @button(label="Help/Support", style=ButtonStyle.gray)
    async def help_support(self, button: Button, interaction: Interaction):
        embed = Embed(title="Help & Support", color=colors.Debug.value)
        embed.add_field(name="About", value="This panel shows your Discord activity statistics and information.")
        embed.add_field(name="Privacy Policy / Terms of Service", value="[Privacy Policy](https://github.com/mahirox36/Negomi/blob/main/Privacy%20Policy.md) / [Terms of Service](https://github.com/mahirox36/Negomi/blob/main/Terms%20of%20Service.md)")
        embed.add_field(name="Support", value="If you need help or want to report issues, contact Me `mahirox36` (that's my username in discord).")
        
        view = BackPanel(self.user)
        await interaction.response.edit_message(embed=embed, view=view)

class BirthdayModal(Modal):
    def __init__(self):
        super().__init__(title="Set Birthday")
        self.year = TextInput(
            label="Year",
            placeholder="YYYY",
            min_length=4,
            max_length=4,
            required=True
        )
        self.month = TextInput(
            label="Month",
            placeholder="MM",
            min_length=1,
            max_length=2,
            required=True
        )
        self.day = TextInput(
            label="Day",
            placeholder="DD",
            min_length=1,
            max_length=2,
            required=True
        )
        self.add_item(self.year)
        self.add_item(self.month)
        self.add_item(self.day)

    async def callback(self, interaction: Interaction):
        try:
            year = int(self.year.value)
            month = int(self.month.value)
            day = int(self.day.value)
            date = datetime(year, month, day)
            
            if date > datetime.now():
                return await interaction.response.send_message("Birthday cannot be in the future!", ephemeral=True)
                
            userData = UserData(interaction.user)
            userData.user_data.birthdate = date
            userData.save()
            
            await interaction.response.send_message("Birthday set successfully!", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Invalid date format! Please use numbers only.", ephemeral=True)

class UserInfoPanel(View):
    def __init__(self, user: Member | User):
        super().__init__(timeout=900)
        self.user = user
        self.userData = UserData(user)

    def create_info_embed(self) -> Embed:
        embed = Embed(title="User Information", color=colors.Info.value)
        embed.add_field(name="Name", value=f"`{self.userData.user_data.name}`")
        embed.add_field(name="Joined Discord", value=f"`{self.userData.user_data.joined_at}`")
        names = ", ".join(self.userData.user_data.unique_names) or "None"
        embed.add_field(name="Previous Names", value=f"`{names}`")
        
        birthday = "Not Set"
        if self.userData.user_data.birthdate:
            birthday = self.userData.user_data.birthdate.strftime("%B %d, %Y")
        embed.add_field(name="Birthday", value=f"`{birthday}`")
        return embed

    @button(label="Set Birthday", style=ButtonStyle.blurple)
    async def set_birthday(self, button: Button, interaction: Interaction):
        modal = BirthdayModal()
        await interaction.response.send_modal(modal)

    @button(label="Request Data", style=ButtonStyle.green)
    async def request_data(self, button: Button, interaction: Interaction):
        data = json.dumps(self.userData.user_data.to_dict(), indent=2)
        file = File(io.StringIO(data), filename=f"user_data_{self.user.id}.json")
        await interaction.response.send_message("Here's your data:", file=file, ephemeral=True)

    @button(label="Delete Data", style=ButtonStyle.red)
    async def delete_data(self, button: Button, interaction: Interaction):
        embed = Embed(title="⚠️ Confirm Data Deletion", color=colors.Error.value)
        embed.description = "Are you sure you want to delete all your data? This cannot be undone."
        
        view = ConfirmDelete(self.user)
        await interaction.response.edit_message(embed=embed, view=view)

    @button(label="Back", style=ButtonStyle.gray)
    async def back(self, button: Button, interaction: Interaction):
        embed = Embed(title="Account Panel", color=colors.Info.value)
        embed.description = "Select an option below"
        
        view = MainPanel(self.user)
        await interaction.response.edit_message(embed=embed, view=view)

class ConfirmDelete(View):
    def __init__(self, user: Member | User):
        super().__init__(timeout=120)
        self.user = user
        self.userData = UserData(user)

    @button(label="Confirm Delete", style=ButtonStyle.red)
    async def confirm(self, button: Button, interaction: Interaction):
        self.userData.delete()
        await interaction.response.edit_message(content="Your data has been deleted.", embed=None, view=None)

    @button(label="Cancel", style=ButtonStyle.gray)
    async def cancel(self, button: Button, interaction: Interaction):
        view = UserInfoPanel(self.user)
        await interaction.response.edit_message(embed=view.create_info_embed(), view=view)

class BackPanel(View):
    def __init__(self, user: Member | User):
        super().__init__(timeout=900)
        self.user = user

    @button(label="Back", style=ButtonStyle.gray)
    async def back(self, button: Button, interaction: Interaction):
        embed = Embed(title="Account Panel", color=colors.Info.value)
        embed.description = "Select an option below"
        
        view = MainPanel(self.user)
        await interaction.response.edit_message(embed=embed, view=view)

class Account(commands.Cog):
    def __init__(self, client:Bot):
        self.client = client
        
    @commands.Cog.listener()
    async def on_message(self, message:Message):
        if message.author.id == self.client.user.id:
            user_manager = UserData(self.client.user)
            user_manager.record_bot_message()
            
        if message.author.bot:
            return
        userData = UserData(message.author)
        await userData.incrementMessageCount(message)
    
    @commands.Cog.listener()
    async def on_application_command_completion(self, ctx: init):
        user_manager = UserData(self.client.user)
        user_manager.record_command_processed(ctx.application_command.name)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: init, error: Exception):
        user_manager = UserData(self.client.user)
        user_manager.record_error(ctx.application_command.name, str(error))
    
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction:Reaction, user: Member | User):
        if user.bot:
            return
        userData = UserData(user)
        userData.user_data.reactions_given += 1
        userData.save()
        userData= UserData(reaction.message.author)
        userData.user_data.reactions_received += 1
        userData.save()
    
    @commands.Cog.listener()
    async def on_message_delete(self, message:Message):
        if message.author.bot:
            return
        userData = UserData(message.author)
        userData.user_data.deleted_messages += 1
        userData.save()
    
    @commands.Cog.listener()
    async def on_message_edit(self, before:Message, after:Message):
        if after.author.bot:
            return
        userData = UserData(after.author)
        userData.user_data.deleted_messages += 1
        userData.save()
    
    @commands.Cog.listener()
    async def on_interaction(self, ctx: init):
        await UserData.commandCount(ctx)
    
    @slash_command(name="account", description="View your account information and statistics")
    async def account(self, interaction: Interaction):
        embed = Embed(title="Account Panel", color=colors.Info.value)
        embed.description = "Select an option below"
        
        view = MainPanel(interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

def setup(client):
    client.add_cog(Account(client))