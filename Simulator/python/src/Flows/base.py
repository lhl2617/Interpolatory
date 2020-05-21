# Base classes for optical flow estimators

class BaseFlow(object):
    def __init__(self):
        return

    def get_flow(self, image_1, image_2):
        raise NotImplementedError('To be implemented by derived classes')