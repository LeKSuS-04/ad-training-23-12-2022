from asyncio import StreamReader, StreamWriter
from storage import AbstractStorage, StorageException
from utils import get_unused_emojies, add_decoration, random_string


ACTIONS_PROMPT = '''
=***= What do you want to do? =***=
1. 🆕 Create new tree
2. 🎀 Add decorations to existing tree
3. 🌲 List undecorated trees
4. 🎄 List decorated trees
5. 🎁 View presents under the tree
6. 👋 Exit
> '''

EMPTY_TREE = r'''
         A
        {*}
         V
        d$b
      .d\$$b.
    .{*}i$$\$$b.
       d$$@b
      d\$${*}
    .d$$$\$$$b
  .d$${*}$$\$$ib.
      d$$i$$b {*}
     d\$$$$@$b
  .d{*}$\$$$$$@b.
.d$$$$i$$$\{*}$$$b.
        ###
        ###
        ###
'''


class ChristmojiHandler:
    def __init__(
        self, reader: StreamReader, writer: StreamWriter, storage: AbstractStorage
    ):
        self.reader = reader
        self.writer = writer
        self.storage = storage

    async def send_message(self, message: str):
        self.writer.write(message.encode())
        await self.writer.drain()

    async def read_message(self) -> str:
        return (await self.reader.read(4096)).strip().decode()

    async def read_with_message(self, message: str) -> str:
        await self.send_message(message)
        return await self.read_message()

    async def prompt_for_choice(
        self, prompt: str, min_option: int, max_option: int
    ) -> int:
        available_options = [str(i) for i in range(min_option, max_option + 1)]
        while True:
            client_choice = await self.read_with_message(prompt)
            if client_choice in available_options:
                return int(client_choice)
            else:
                await self.send_message(
                    f'Ho-ho-ho 🎅, bad option! Expected number between {min_option} and {max_option}, try again:\n'
                )

    async def create_tree(self):
        if self.storage.size('undecorated_trees') > 10:
            await self.send_message(
                'There are a lot of undecorated trees! Go check them out 😃!'
            )
            return

        tree_id = random_string(24)
        password = await self.read_with_message('Enter password to your tree: ')
        self.storage.store('passwords', tree_id, password)
        self.storage.store('undecorated_trees', tree_id, EMPTY_TREE)
        await self.send_message(f'Done! Your tree id is {tree_id}!\n')

    async def add_decorations(self):
        tree_id = await self.read_with_message('Which tree you want to decorate 🌲🌳🌴?: ')
        try:
            tree = self.storage.get('undecorated_trees', tree_id)
            if not tree:
                await self.send_message('Tree not found 🔎 \n')
                return
        except StorageException:
            await self.send_message('Something went wrong 🥴\n')
            return

        emojies = get_unused_emojies(tree, 5)
        prompt = 'Which emoji do you want to use 😋?\n'
        for i, emoji in enumerate(emojies):
            prompt += f'{i+1}. {emoji}\n'
        prompt += '> '

        emoji_idx = (await self.prompt_for_choice(prompt, 1, len(emojies))) - 1
        emoji = emojies[emoji_idx]
        tree = add_decoration(tree, emoji)
        if '{*}' in tree:
            self.storage.store('undecorated_trees', tree_id, tree)
        else:
            self.storage.remove('undecorated_trees', tree_id)
            self.storage.store('decorated_trees', tree_id, tree)

        want_present = await self.read_with_message(
            'Do you want to leave a present 🎁? (y/n): '
        )
        if want_present.lower() not in ['y', 'yes']:
            await self.send_message(f'Ok! Take a look at the tree:\n{tree}')
            return

        present = await self.read_with_message('Enter text of your present: ')
        presents_collection = f'{tree_id}_presents'
        self.storage.store(presents_collection, emoji, present)
        await self.send_message('Thank you! Your present is stored 🫙!\n')

    async def list_undecorated(self):
        undecorated_trees = self.storage.list('undecorated_trees')
        if len(undecorated_trees) == 0:
            message = 'There are no undecorated trees 😨!\n'
        else:
            message = "Here's the list of undecorated trees ids 🌲:\n"
            for tree_id in undecorated_trees:
                message += f'- {tree_id}\n'
        await self.send_message(message)

    async def list_decorated(self):
        decorated_trees = self.storage.list('undecorated_trees')
        if len(decorated_trees) == 0:
            message = 'There are no decorated trees 😨!\n'
        else:
            message = "Here's the list of decorated trees' ids 🎄:\n"
            for tree_id in decorated_trees:
                message += f'- {tree_id}\n'
        await self.send_message(message)

    async def view_presents(self):
        tree_id = await self.read_with_message('Enter tree id: ')
        password = await self.read_with_message('Enter tree password: ')

        try:
            real_password = self.storage.get('passwords', tree_id)
            if real_password != password:
                await self.send_message('Wrong password ⛔!\n')
                return

            presents_collection = f'{tree_id}_presents'
            present_keys = self.storage.list(presents_collection)
            message = "Here are your presents:\n"
            for present_key in present_keys:
                present = self.storage.get(presents_collection, present_key)
                message += f'- ({present_key}): {present}\n'
            await self.send_message(message)

        except StorageException:
            await self.send_message('Something went wrong 🥴\n')

    async def loop(self):
        await self.send_message('*** ⛄ Hello ⛄ ***\n')

        while True:
            action = await self.prompt_for_choice(ACTIONS_PROMPT, 1, 5)
            match action:
                case 1:
                    await self.create_tree()
                case 2:
                    await self.add_decorations()
                case 3:
                    await self.list_undecorated()
                case 4:
                    await self.list_decorated()
                case 5:
                    await self.view_presents()
                case 6:
                    break

        await self.send_message('Bye!\n')
        self.writer.close()
        await self.writer.wait_closed()
