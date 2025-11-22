import os
import sys

'''
@ Checkpoint Tag
---
O Get
+ Mix
X Fix
V Cut
> Slice
] Box
# Size
= Ship
'''

def get_file_path(filename):
    """
    Get the absolute path of a file in the current directory.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, filename)
