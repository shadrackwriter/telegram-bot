#!env/bin/python

import re
import logging
import sys

import telebot

from lkb_redis import LKBRedis

TAG_EXACT_REGEX = re.compile(r'^[#/]\S+$')
HASH_TAG_REGEX = re.compile(r'#\S+')
SECONDS_PER_DAY = 60 * 60 * 24

logger = logging.getLogger('LKB')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

bot = telebot.TeleBot(LKBRedis().get('bot_token'))


@bot.message_handler(commands=['start', 'help'])
def show_help(message):
    bot.send_message(
        message.from_user.id,
        'Send me any text message with hash tag and I will store it for a day. '
        'You can then retrieve it using the same tag.')


@bot.message_handler(commands=['tags'])
def show_tags_list(message):
    logger.info('Tags command, user_id='.format(message.from_user.id))
    bot.send_message(
        message.from_user.id,
        '\n'.join(
            '/{}'.format(tag) for tag in
            LKBRedis().hkeys(message.from_user.id))
        or 'Sorry, there are no tags yet.')


@bot.message_handler(func=lambda msg: TAG_EXACT_REGEX.match(msg.text))
def show_messages_by_tag(message):
    logger.info('Show messages, user_id={}'.format(message.from_user.id))
    tag = TAG_EXACT_REGEX.search(message.text).group(0)[1:]
    redis_conn = LKBRedis()
    notes_set_key = redis_conn.hget(message.from_user.id, tag)
    notes = []
    if notes_set_key is not None:
        for note_key in redis_conn.smembers(notes_set_key):
            note = redis_conn.get(note_key)
            if note is None:
                redis_conn.srem(notes_set_key, note_key)
            else:
                notes.append(note)
    if not notes:
        bot.send_message(
            message.from_user.id,
            'Sorry, there are now notes for #{} tag.'.format(tag))
        logger.info('No notes for tag #{}'.format(tag))
        redis_conn.hdel(message.from_user.id, tag)
    else:
        bot.send_message(message.from_user.id, '\n-----\n'.join(notes))
        logger.info('Success')


@bot.message_handler()
def text_handler(message):
    logger.info('New note, user_id={}'.format(message.from_user.id))
    redis_conn = LKBRedis()
    tags = HASH_TAG_REGEX.findall(message.text)
    if '#tags' in tags or '#start' in tags or '#help' in tags:
        bot.send_message(
            message.from_user.id,
            'Sorry, you cannot use tags #tags, #help or #start, '
            'because they are reserved for commands: /tags, /help, /start.')
        logger.info('Unavailable tags')
        return
    if not tags:
        bot.send_message(
            message.from_user.id,
            'Sorry, no tags have been parsed in your msg.')
        logger.info('No tags')
        return
    for tag in tags:
        tag = tag[1:]
        note_key = LKBRedis.get_new_note_key(message.from_user.id)
        redis_conn.set(note_key, message.text, ex=SECONDS_PER_DAY)
        notes_set_key = \
            redis_conn.hget(message.from_user.id, tag) \
            or LKBRedis.get_notes_set_key(message.from_user.id, tag)
        redis_conn.sadd(notes_set_key, note_key)
        redis_conn.hset(message.from_user.id, tag, notes_set_key)
    bot.send_message(
        message.from_user.id,
        'Done! You can retrieve list of all tags using /tags command.')
    logger.info('Success')

if __name__ == '__main__':
    telebot.logger.setLevel(logging.INFO)
    bot.polling(none_stop=True)
