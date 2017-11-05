# encoding: utf-8

import os
from contextlib import contextmanager

from redlock import Redlock, Lock

REDIS_HOST = os.environ.get('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_DB = 1
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', 'password')


class AcquireLockError(Exception):
    """
    获取锁失败
    """


@contextmanager
def dlock(key, ttl, **kwargs):
    """
    分布式锁
    :param key: 分布式锁ID
    :param ttl: 分布式锁生存时间
    :param kwargs: 可选参数字典
    :return: None
    """
    resource_servers = [
        {
            'host': REDIS_HOST,
            'port': REDIS_PORT,
            'db': REDIS_DB,
            'password': REDIS_PASSWORD
        }
    ]
    dl = Redlock(resource_servers)
    # 获取锁
    lock = dl.lock(key, ttl)
    # if ret is False:
    #     detail = u'acquire lock[%s] error' % key
    #     raise AcquireLockError(detail)

    yield lock

    # 释放锁
    if isinstance(lock, Lock):
        dl.unlock(lock)


if __name__ == '__main__':
    import threading

    def fake():
        with dlock('test1111', 5000) as lock:
            if lock is False:
                print('acquire lock error')
                return

            import time
            print('before call fake func')
            time.sleep(3)
            print('after call fake func')


    t1 = threading.Thread(target=fake)
    t1.setDaemon(True)
    t2 = threading.Thread(target=fake)
    t2.setDaemon(True)

    t1.start()
    t2.start()

    t1.join()
    t2.join()
