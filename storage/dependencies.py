from storage.local_storage import LocalStorage

_storage = LocalStorage()


def get_storage() -> LocalStorage:
    return _storage