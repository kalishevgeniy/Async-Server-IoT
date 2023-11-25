import asyncio


class ClientConnectionsKeeper:
    def __init__(self):
        self._set_task = set()

    def add(self, task):
        self._set_task.add(task)

    def remove_curr_task(self, task):
        self._set_task.remove(task)

    @staticmethod
    async def _stop(task):
        """
        Stop client socket
        If socket not close after timeout, make extraordinary stop
        :param task: asyncio.Task
        :return:
        """
        try:
            await asyncio.wait_for(task, 30)
        except asyncio.TimeoutError:
            print(f"Warning! Task {task} Need cancel")
            task.cancel()

    async def try_stop(self):
        async with asyncio.TaskGroup() as tg:
            for task in self._set_task:
                tg.create_task(self._stop(task))
        return True
