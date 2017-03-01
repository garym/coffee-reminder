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

radio.on()
radio.config(power=1, channel=88, address=0x45696277)

cup = '93399:93399:59950'
status = {}


def cuptop():
    rowchoice = ['07000:', '00700:']
    row1, row2 = rowchoice
    while True:
        yield row1 + row2
        if random.random() > 0.6:
            rowchoice = rowchoice[::-1]
        row1, row2 = row2, rowchoice[0]


cuptopgen = cuptop()
coffee = [Image(next(cuptopgen) + cup) for i in range(17)]

throb_base = Image('90000:00000:00000:00000:00000')
throb = [throb_base * (i / 9) for i in range(1, 9)]
throb += [throb_base * (i / 9) for i in range(8, -1, -1)]


def reset():
    display.clear()
    status['last_reset'] = running_time()
    status['clear'] = True
    status['last_heartbeat'] = 0


def spinner():
    display.show(
        [Image.SAD * (i / 9) for i in range(0, 9)],
        delay=500, wait=False, loop=True, clear=False)


def alert():
    display.show(
        coffee, delay=200, wait=False, loop=True, clear=False)
    status['clear'] = False


def heartbeat():
    status['last_heartbeat'] = running_time()
    display.show(
        throb, delay=100, wait=False, loop=False, clear=False)


reset()

while True:
    # Button A and B held down sends an "alert" message.
    # Button A and B clicked sends the "reset" message.
    if status['clear'] and button_a.is_pressed() and button_b.is_pressed():
        spinner()
        radio.send(ALERT_MESSAGE + RESEND_MESSAGE)
    elif button_a.was_pressed() or button_b.was_pressed():
        spinner()
        radio.send(RESET_MESSAGE + RESEND_MESSAGE)

    if status['clear'] and running_time() > status['last_reset'] + ALERT_DELAY:
        spinner()
        radio.send(ALERT_MESSAGE+RESEND_MESSAGE)

    if status['clear'] and running_time() > status['last_heartbeat'] + HEARTBEAT_PERIOD:
        spinner()
        radio.send(HEARTBEAT_MESSAGE + RESEND_MESSAGE)

    # Read any incoming messages.
    incoming = radio.receive()

    if incoming:
        if incoming.startswith(RESET_MESSAGE):
            reset()
        if incoming.startswith(ALERT_MESSAGE):
            alert()
        if incoming.startswith(HEARTBEAT_MESSAGE):
            heartbeat()
        if incoming.endswith(RESEND_MESSAGE):
            radio.send(incoming[:-len(RESEND_MESSAGE)])
