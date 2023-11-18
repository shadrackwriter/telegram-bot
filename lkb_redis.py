from datetime import datetime

from redis import StrictRedis

__all__ = ('LKBRedis', 'KEY_TEMPLATE')

KEY_TEMPLATE = 'LKB:{}'


def _encode(value):
    if isinstance(value, str):
        return value.encode()
    return value


def _decode(value):
    if value is None:
        return None
    return value.decode()


class LKBRedis:
    instance = None

    def __init__(self):
        if LKBRedis.instance is None:
            LKBRedis.instance = LKBRedis.__LKBRedis()

    def __getattr__(self, item):
        return getattr(self.instance, item)

    class __LKBRedis(StrictRedis):
        def __init__(self):
            super(LKBRedis.__LKBRedis, self).__init__(db=2)

        def get(self, name):
            return _decode(
                super(LKBRedis.__LKBRedis, self).get(KEY_TEMPLATE.format(name)))

        def set(self, name, value, *args, **kwargs):
            return super(LKBRedis.__LKBRedis, self).set(
                KEY_TEMPLATE.format(name), _encode(value), *args, **kwargs)

        def delete(self, *names):
            return super(LKBRedis.__LKBRedis, self).delete(
                *(KEY_TEMPLATE.format(name) for name in names))

        def sadd(self, name, *values):
            return super(LKBRedis.__LKBRedis, self).sadd(
                KEY_TEMPLATE.format(name), *map(_encode, values))

        def srem(self, name, *values):
            return super(LKBRedis.__LKBRedis, self).srem(
                KEY_TEMPLATE.format(name), *map(_encode, values))

        def smembers(self, name):
            return map(
                _decode,
                super(LKBRedis.__LKBRedis, self).smembers(
                    KEY_TEMPLATE.format(name)))

        def hset(self, name, key, value):
            return super(LKBRedis.__LKBRedis, self).hset(
                KEY_TEMPLATE.format(name), _encode(key), _encode(value))

        def hget(self, name, key):
            return _decode(
                super(LKBRedis.__LKBRedis, self).hget(
                    KEY_TEMPLATE.format(name), _encode(key)))

        def hdel(self, name, *keys):
            return super(LKBRedis.__LKBRedis, self).hdel(
                KEY_TEMPLATE.format(name), *map(_encode, keys))

        def hkeys(self, name):
            return map(
                _decode,
                super(LKBRedis.__LKBRedis, self).hkeys(
                    KEY_TEMPLATE.format(name)))

    @staticmethod
    def get_notes_set_key(user_id, tag):
        return '{user_id}_{tag}'.format(user_id=user_id, tag=tag)

    @staticmethod
    def get_new_note_key(user_id):
        return '{user_id}_{timestamp}'.format(
            user_id=user_id, timestamp=datetime.now().timestamp())
