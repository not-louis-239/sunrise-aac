# speak.py - module for speaking functionality using pyttsx3

# repo at: https://github.com/not-louis-239/sunrise-aac
# Copyright (C) 2026 Louis Masarei-Boulton <243234869+not-louis-239@users.noreply.github.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# type: ignore

import queue
import time
import threading

import pyttsx3

# Global control queue to pass messages to our speech thread
# Formats sent: ("SPEAK", text) or ("STOP", None)
_speech_queue = queue.Queue()
_engine_ready = threading.Event()


def _speech_worker():
    """Dedicated background thread that owns the TTS engine loop."""

    engine = pyttsx3.init()
    _engine_ready.set()

    while True:
        try:
            # Check for a command. timeout=0.1 allows the loop to stay responsive
            command, text = _speech_queue.get(timeout=0.1)

            if command == "SPEAK":
                try:
                    engine.stop()  # type: ignore
                    del engine     # type: ignore

                    # we need `del` here otherwise we get weird bugs
                    # with the speech cutting off or not playing
                    # so suck it, Pyright!
                except Exception:
                    pass

                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
            elif command == "STOP":
                try:
                    engine.stop()  # type: ignore
                except Exception:
                    pass

            _speech_queue.task_done()
        except queue.Empty:
            continue


# Start the dedicated voice manager thread immediately
threading.Thread(target=_speech_worker, daemon=True).start()


def speak(s: str) -> None:
    """Speaks a given string of text, stopping any speech
    that is already currently playing.
    Safe for rapid navigation and high-speed AAC grid usage."""

    _engine_ready.wait()

    while not _speech_queue.empty():
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except queue.Empty:
            break

    _speech_queue.put(("SPEAK", s))


def stop_speaking() -> None:
    """Stops any currently playing speech immediately."""
    _engine_ready.wait()

    while not _speech_queue.empty():
        try:
            _speech_queue.get_nowait()
            _speech_queue.task_done()
        except queue.Empty:
            break

    _speech_queue.put(("STOP", None))


def _test():
    # Test of three speak commands in quick succession
    speak("First sentence.")
    time.sleep(0.5)
    speak("Second sentence.")
    time.sleep(0.5)
    speak("Third sentence.")

    print("Main thread running... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping script.")


if __name__ == "__main__":
    _test()
