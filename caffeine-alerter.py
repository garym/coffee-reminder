import radio
import random
from microbit import button_a, button_b, display, Image, running_time

HOUR = 60 * 60 * 1000
ALERT_DELAY = 8 * HOUR
HEARTBEAT_PERIOD = 10000

RESET_MESSAGE = 'reset'
ALERT_MESSAGE = 'alert'
HEARTBEAT_MESSAGE = 'heartbeat'
RESEND_MESSAGE = '_resend'

radio.config(power=1, address=0x45696277)
radio.on()

status = {
    'apply_status': True,
}


def cuptop():
    rowchoice = ['07000:', '00700:']
    row1, row2 = rowchoice
    while True:
        yield row1 + row2
        if random.random() > 0.6:
            rowchoice = rowchoice[::-1]
        row1, row2 = row2, rowchoice[0]


def reset():
    display.clear()
    status.update({
        'showing_error': False,
        'last_reset': running_time(),
        'last_heartbeat': 0,
        'status': HEARTBEAT_MESSAGE,
    })


def spinner():
    display.show(
        [Image.SAD * (i / 9) for i in range(0, 9)],
        delay=500, wait=False, loop=True, clear=False)


def alert():
    cup = '93399:93399:09900'
    cuptopgen = cuptop()
    image = [Image(next(cuptopgen) + cup) for i in range(17)]
    display.show(
        image, delay=200, wait=False, loop=True, clear=False)


def heartbeat():
    status['last_heartbeat'] = running_time()
    throb_base = Image('90000:00000:00000:00000:00000')
    throb = [throb_base * (i / 9) for i in range(1, 9)]
    throb += [throb_base * (i / 9) for i in range(8, -1, -1)]

    display.show(
        throb, delay=100, wait=False, loop=False, clear=False)


def send_and_expect_response(msg):
    spinner()
    radio.send(msg + RESEND_MESSAGE)


reset()


def process_local_generated_events():
    if button_b.was_pressed():
        send_and_expect_response(RESET_MESSAGE)
    elif button_a.was_pressed():
        send_and_expect_response(ALERT_MESSAGE)
    elif status['status'] != ALERT_MESSAGE:
        if running_time() > status['last_reset'] + ALERT_DELAY:
            send_and_expect_response(ALERT_MESSAGE)
        if running_time() > status['last_heartbeat'] + HEARTBEAT_PERIOD:
            send_and_expect_response(HEARTBEAT_MESSAGE)


while True:
    process_local_generated_events()
    try:
        incoming = radio.receive()
    except ValueError:
        spinner()
        continue

    if incoming:
        resend = incoming.endswith(RESEND_MESSAGE)
        msg = incoming[:-len(RESEND_MESSAGE)] if resend else incoming
        if msg in (RESET_MESSAGE, ALERT_MESSAGE, HEARTBEAT_MESSAGE):
            status['status'] = msg
            status['apply_status'] = True
        if resend:
            radio.send(msg)

    if status['apply_status']:
        status['apply_status'] = False
        msg = status['status']
        if msg == RESET_MESSAGE:
            reset()
        elif msg == ALERT_MESSAGE:
            alert()
        elif msg == HEARTBEAT_MESSAGE:
            heartbeat()
