import os
import signal
from decimal import Decimal
# Captcha
from captcha.image import ImageCaptcha
from random import randint
import base64


def decimal_to_string(value, exponent=6):
    rounded = round(Decimal(value), exponent)
    rounded_str = str(rounded)
    #strip = rounded_str.rstrip("0")
    #if strip[-1] == ".":
    #    strip = strip[0:-1]
    #return strip
    return rounded_str

def get_captcha():
    ic = ImageCaptcha(width = 224, height = 72)
    solution = str(randint(0, 99999)).zfill(5)
    data = ic.generate(solution)
    data.seek(0)
    return {
        "image": base64.b64encode(data.getvalue()).decode(),
        "solution": solution,
    }


class ExitHandler:
    do_exit = False
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_requested)
        signal.signal(signal.SIGTERM, self.exit_requested)
    
    def exit_requested(self, *args):
        self.do_exit = True


class DeferSignals():
    """
    Context manager to defer signal handling until context exits.
    Takes optional list of signals to defer (default: SIGHUP, SIGINT, SIGTERM).
    Signals can be identified by number or by name.
    Allows you to wrap instruction sequences that ought to be atomic and ensure
    that they don't get interrupted mid-way.
    """

    def __init__(self, signal_list=None):
        # Default list of signals to defer
        if signal_list is None:
            signal_list = [signal.SIGHUP, signal.SIGINT, signal.SIGTERM]
        # Accept either signal numbers or string identifiers
        self.signal_list = [
            getattr(signal, sig_id) if isinstance(sig_id, str) else sig_id
            for sig_id in signal_list
        ]
        self.deferred = []
        self.previous_handlers = {}

    def defer_signal(self, sig_num, stack_frame):
        self.deferred.append(sig_num)

    def __enter__(self):
        # Replace existing handlers with deferred handler
        for sig_num in self.signal_list:
            # signal.signal returns None when no handler has been set in Python,
            # which is the same as the default handler (SIG_DFL) being set
            self.previous_handlers[sig_num] = (
                signal.signal(sig_num, self.defer_signal) or signal.SIG_DFL)
        return self

    def __exit__(self, *args):
        # Restore handlers
        for sig_num, handler in self.previous_handlers.items():
            signal.signal(sig_num, handler)
        # Send deferred signals
        while self.deferred:
            sig_num = self.deferred.pop(0)
            os.kill(os.getpid(), sig_num)

    def __call__(self):
        """
        If there are any deferred signals pending, trigger them now
        This means that instead of this code:
            for item in collection:
                with defer_signals():
                    item.process()
        You can write this:
            with defer_signals() as handle_signals:
                for item in collection:
                    item.process()
                    handle_signals()
        Which has the same effect but avoids having to embed the context
        manager in the loop
        """
        if self.deferred:
            # Reattach the signal handlers and fire signals
            self.__exit__()
            # Put our deferred signal handlers back in place
            self.__enter__()