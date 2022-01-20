from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from unittest import TestCase
from unittest.mock import Mock, call, patch
from progress import Progress

class ProgressTest(TestCase):

    def test_construct(self):
        logger = Mock()
        pl = Progress(logger)


    def test_debug_is_called(self):
        logger = Mock()
        pl = Progress(logger)
        pl.debug('foo')
        logger.log.assert_called_once_with(DEBUG, 'foo')


    def test_info_is_called(self):
        logger = Mock()
        pl = Progress(logger)
        pl.info('foo')
        logger.log.assert_called_once_with(INFO, 'foo')


    def test_warning_is_called(self):
        logger = Mock()
        pl = Progress(logger)
        pl.warning('foo')
        logger.log.assert_called_once_with(WARNING, 'foo')


    def test_error_is_called(self):
        logger = Mock()
        pl = Progress(logger)
        pl.error('foo')
        logger.log.assert_called_once_with(ERROR, 'foo')


    def test_critical_is_called(self):
        logger = Mock()
        pl = Progress(logger)
        pl.critical('foo')
        logger.log.assert_called_once_with(CRITICAL, 'foo')


    def test_count_must_be_a_positive_integer(self):
        logger = Mock()
        with self.assertRaisesRegex(ValueError, 'positive integer'):
            Progress(logger, count=0)


    def test_logger_is_called_every_count_calls(self):
        logger = Mock()
        pl = Progress(logger, count=2)
        pl.info('1')
        pl.info('2')
        pl.info('3')
        pl.info('4')
        pl.info('5')
        logger.log.assert_has_calls([call(INFO, '2'), call(INFO, '4')])


    def test_delay_must_be_positive(self):
        logger = Mock()
        with self.assertRaisesRegex(ValueError, 'must be >= 0'):
            Progress(logger, delay=-1)


    def test_logger_is_called_after_delay(self):
        logger = Mock()
        with patch('progress.time', autospec=True) as clock:
            clock.side_effect = [0.0, 0.5, 2.0]
            pl = Progress(logger, delay=1)
            pl.info('1')
            pl.info('2')
            logger.log.assert_has_calls([call(INFO, '2')])
