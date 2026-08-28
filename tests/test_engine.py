import unittest
from oes32_engine import evaluate, fold8_residual, residual, symmetry_residual

class EngineTests(unittest.TestCase):
    def test_zero_state_is_safe(self):
        result = evaluate([0] * 32, [0] * 32)
        self.assertTrue(result.safe)
        self.assertFalse(result.latch)

    def test_residual_is_max_absolute_deviation(self):
        x = [0] * 32
        x[7] = -0.2
        self.assertAlmostEqual(residual(x, [0] * 32), 0.2)

    def test_threshold_equality_is_accepted(self):
        x = [0] * 32
        x[0] = 0.08
        result = evaluate(x, [0] * 32)
        self.assertFalse(result.latch)
        self.assertLessEqual(result.residual, 0.08)

    def test_threshold_exceedance_latches(self):
        x = [0] * 32
        x[0] = 0.080001
        self.assertTrue(evaluate(x, [0] * 32).latch)

    def test_fold8_wraparound(self):
        x = [0] * 32
        x[7] = 0.2
        self.assertAlmostEqual(fold8_residual(x), 0.2)

    def test_even_and_odd_symmetry_convention(self):
        x = [0] * 32
        for i in range(16):
            x[i] = 1
            x[i + 16] = 1 if i % 2 == 0 else -1
        self.assertEqual(symmetry_residual(x, 0), 0)
        self.assertEqual(symmetry_residual(x, 1), 0)

    def test_invalid_width_rejected(self):
        with self.assertRaises(ValueError):
            evaluate([0] * 31, [0] * 32)

if __name__ == "__main__":
    unittest.main()
