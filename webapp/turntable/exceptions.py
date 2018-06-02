# encoding: utf-8

class BusinessException(Exception):
    pass


class DuplicateUserException(BusinessException):
    pass

class InvalidProducerException(BusinessException):
    pass

class NchanCommunicationError(BusinessException):
    pass

class MaxNumberOfPivotReachedException(BusinessException):
    pass

class MaxNumberOfProducerReachedException(BusinessException):
    pass

class MaxNumberOfConsumerReachedException(BusinessException):
    pass
