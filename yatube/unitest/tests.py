import unittest
from codes import series_sum


class TestSeriesSum(unittest.TestCase):
    """Тестируем series_sum."""

    def test_mixed_number(self):
        call = series_sum([1, 2.5, 3, 4])
        result = '12.534'
        self.assertEqual(
            call, result, 'Функция series_sum() не работает со списком чисел'
        )

    def test_mixed_numbers_strings(self):
        call = series_sum([1, 'fff', 3, 4])
        result = '1fff34'
        self.assertEqual(
            call, result, 'Функция series_sum не работает со смешанным списком'
        )

    def test_empty(self):
        call = series_sum([''])
        result = ''
        self.assertEqual(
            call, result, 'Функция series_sum не работает с пустым списком'
        )


if __name__ == '__main__':
    unittest.main()
