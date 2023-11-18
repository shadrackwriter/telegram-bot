import unittest

from lkb_redis import LKBRedis


class LKBRedisTestCase(unittest.TestCase):
    def setUp(self):
        self.redis = LKBRedis()
        self.redis.delete('test_key', 'test_hash', 'test_set')

    def test_key(self):
        self.assertEqual(self.redis.set('test_key', 'abc'), 1)
        self.assertEqual(self.redis.get('test_key'), 'abc')
        self.assertEqual(self.redis.delete('test_key'), 1)

    def test_hash(self):
        self.assertEqual(self.redis.hset('test_hash', 'abc', 'def'), 1)
        self.assertEqual(self.redis.hget('test_hash', 'abc'), 'def')
        self.assertEqual(self.redis.hset('test_hash', 'abc', 'nop'), 0)
        self.assertEqual(self.redis.hget('test_hash', 'abc'), 'nop')
        self.assertEqual(self.redis.hset('test_hash', 'hij', 'klm'), 1)
        self.assertEqual(
            set(self.redis.hkeys('test_hash')),
            {'abc', 'hij'})
        self.assertEqual(self.redis.hdel('test_hash', 'abc'), 1)
        self.assertEqual(self.redis.hget('test_hash', 'abc'), None)
        self.assertEqual(self.redis.delete('test_hash'), 1)

    def test_set(self):
        self.assertEqual(self.redis.sadd('test_set', 'abc', '123'), 2)
        self.assertEqual(
            set(self.redis.smembers('test_set')),
            {'abc', '123'})
        self.assertEqual(self.redis.srem('test_set', 'abc'), 1)
        self.assertEqual(self.redis.delete('test_set'), 1)

if __name__ == '__main__':
    unittest.main()
