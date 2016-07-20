#!/usr/bin/python

class LockGuard():
    """An auto-release Lock Guard, only support threading.RLock currently"""
    def __init__(self, lock):
        self.lock = lock
        self.lock.acquire()
    def __del__(self):
        self.lock.release()