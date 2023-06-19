import copy
import random
import discord

marks = ['♣️', '♠️', '❤️', '♦️']
numbers = range(1, 14)
trump_cards = ['{} {}'.format(m, n) for m in marks for n in numbers]

num_cards = list(range(1,101))

salt = 2938267023354395738

class DeckView(discord.ui.View):
    def __init__(self, args, timeout):
        super().__init__(timeout=timeout)

        for txt in args:
            self.add_item(DeckButton(txt))

class DeckButton(discord.ui.Button):
    def __init__(self, txt):
        super().__init__(style=discord.ButtonStyle.blurple, label=txt)

    async def callback(self, interaction): #デッキを表示
        if self.label=='トランプ':
            res_view = TopView('trump', 52, timeout=None)
        else:
            res_view = TopView(100, 100, timeout=None)
        res_msg = '青いボタンを押すと手札を作れます。青いボタンの数字はデッキの枚数です。'

        # スレッドを作成し、デッキを送信
        thread = await interaction.message.create_thread(name='Deck Thread')
        await thread.send(res_msg, view=res_view)
        await interaction.response.send_message('デッキを作ったよ！スレッドを確認してみてね。')

class TopView(discord.ui.View): # デッキトップのボタンのクラス
    def __init__(self, arg, deck_num, timeout):
        super().__init__(timeout=timeout)

        if arg == 'trump':
            custom_id = arg
        else:
            custom_id = 'number'
        self.add_item(TopButton(deck_num, custom_id))
        self.add_item(PutFieldButton())

class TopButton(discord.ui.Button):
    def __init__(self, num, custom_id):
        super().__init__(style=discord.ButtonStyle.blurple, custom_id=custom_id, label=str(num))

    async def callback(self, interaction):
        # 山札を取得
        components=interaction.message.components[0].children
        for cpnt in components:
            if cpnt.custom_id == 'trump':
                cards = copy.copy(trump_cards)
                deck_type = cpnt.custom_id
                but = cpnt
            
            if cpnt.custom_id == 'number':
                cards = copy.copy(num_cards)
                deck_type = cpnt.custom_id
                but = cpnt
        # メッセージIDをシード値にシャッフル
        random.seed(interaction.message.id+salt)
        random.shuffle(cards)
        # 残り枚数を取得
        num = int(but.label)
        # トップのカードを手札に
        hand = cards[num-1]
        # 元のメッセージを編集して1枚減らす
        await interaction.message.edit(content='青いボタンを押すと手札を作れます。青いボタンの数字はデッキの枚数です。', view=TopView(deck_type, num-1, timeout=None))

        # 手札情報を送る
        res_msg = 'あなたの手札です。数字ボタンを押すと場に出します。もう1枚を押すとデッキからドローします。'
        await interaction.response.send_message(res_msg,view=NumberView([hand], timeout=None), ephemeral=True)

class NumberView(discord.ui.View):
    def __init__(self, arg, timeout):
        super().__init__(timeout=timeout)

        for num in arg:
            self.add_item(NumberButton(num))
        self.add_item(DrawButton(custom_id='draw'))

class NumberButton(discord.ui.Button):
    def __init__(self, num):
        super().__init__(label=str(num))

    async def callback(self, interaction):
        cpnt = interaction.data
        interact_id = cpnt['custom_id']

        hands = []
        res_msg = 'あなたの手札です。数字ボタンを押すと場に出します。もう1枚を押すとデッキからドローします。'
        for listcps in interaction.message.components:
            for cps in listcps.children:
                if cps.custom_id == interact_id:
                    destroy_card = cps.label
                    continue
                if cps.custom_id != 'draw':
                    hands.append(cps.label)
        await interaction.channel.send(content='{}は{}を出しました'.format(interaction.user.display_name, destroy_card))
        await interaction.response.edit_message(content=res_msg,view=NumberView(hands, timeout=None))


class DrawButton(discord.ui.Button):
    def __init__(self, custom_id):
        super().__init__(style=discord.ButtonStyle.blurple, label='もう1枚', custom_id=custom_id)

    async def callback(self, interaction):
        # デッキ枚数を減らす
        orig_mess_id = interaction.message.reference.message_id
        orig_mess = await interaction.channel.fetch_message(orig_mess_id)
        # 山札を取得
        components=orig_mess.components[0].children
        for cpnt in components:
            if cpnt.custom_id == 'trump':
                cards = copy.copy(trump_cards)
                deck_type = cpnt.custom_id
                but = cpnt
            
            if cpnt.custom_id == 'number':
                cards = copy.copy(num_cards)
                deck_type = cpnt.custom_id
                but = cpnt
        # メッセージIDをシード値にシャッフル
        random.seed(orig_mess_id+salt)
        random.shuffle(cards)
        # 残り枚数を取得
        num = int(but.label)
        # トップのカードを手札に
        hand = str(cards[num-1])
        # Deckのメッセージを編集して1枚減らす
        await orig_mess.edit(content='青いボタンを押すと手札を作れます。青いボタンの数字はデッキの枚数です。', view=TopView(deck_type, num-1, timeout=None))

        # 手札を増やす
        hands=[]
        for listcps in interaction.message.components:
            for cps in listcps.children:
                if cps.custom_id != 'draw':
                    hands.append(cps.label)
        hands.append(hand)
        # メッセージ決定
        if interaction.message.flags.ephemeral is True:
            res_msg = 'あなたの手札です。数字ボタンを押すと場に出します。もう1枚を押すとデッキからドローします。'
        else:
            res_msg = '場に以下のカードが出されています'
        await interaction.response.edit_message(content=res_msg,view=NumberView(hands, timeout=None))

class PutFieldButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label='場に出す')

    async def callback(self, interaction):
        # 山札を取得
        components=interaction.message.components[0].children
        for cpnt in components:
            if cpnt.custom_id == 'trump':
                cards = copy.copy(trump_cards)
                deck_type = cpnt.custom_id
                but = cpnt
            
            if cpnt.custom_id == 'number':
                cards = copy.copy(num_cards)
                deck_type = cpnt.custom_id
                but = cpnt
        # メッセージIDをシード値にシャッフル
        random.seed(interaction.message.id+salt)
        random.shuffle(cards)
        # 残り枚数を取得
        num = int(but.label)
        # トップのカードを手札に
        hand = cards[num-1]
        # 元のメッセージを編集して1枚減らす
        await interaction.message.edit(content='青いボタンを押すと手札を作れます。青いボタンの数字はデッキの枚数です。', view=TopView(deck_type, num-1, timeout=None))

        # 手札情報を送る
        res_msg = '場に以下のカードが出されています'
        await interaction.response.send_message(res_msg,view=NumberView([hand], timeout=None))
