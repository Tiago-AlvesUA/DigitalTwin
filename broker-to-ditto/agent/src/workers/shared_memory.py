import multiprocessing
import queue
# Shared queue for storing MQTT messages (multiprocessing-safe)
message_queue = multiprocessing.Queue()

messages = queue.Queue()

mjpeg_frames = queue.Queue()


# class SharedQueue:
#     @staticmethod
#     def add_message(message):
#         """Add message to the shared queue."""
#         message_queue.put(message)

#     @staticmethod
#     def get_message():
#         """Retrieve message from the shared queue."""
#         try:
#             message = message_queue.get_nowait()
#         except queue.Empty:
#             message = None
#         return message

#     @staticmethod
#     def is_empty():
#         """Check if the queue is empty."""
#         return message_queue.empty()

#     @staticmethod
#     def clear():
#         """Clear the shared queue."""
#         while not message_queue.empty():
#             message_queue.get_nowait()
