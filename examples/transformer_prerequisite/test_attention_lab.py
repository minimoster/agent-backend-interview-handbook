"""Finite, small arithmetic contracts; no trained-model or GPU claims."""

import copy
import math
import unittest

from attention_lab import (
    add, causal_allowed, demo, feed_forward, identity, layer_norm, linear,
    matmul, multihead_self_attention, scaled_attention, shape, stable_softmax,
    transformer_block,
)


class MatrixTests(unittest.TestCase):
    def test_matrix_multiply(self):
        self.assertEqual(matmul([[1, 2, 3]], [[1, 0], [0, 1], [1, 1]]),
                         [[4, 5]])

    def test_shape_rejects_empty_and_ragged(self):
        for bad in ([], [[]], [[1], [1, 2]]):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                shape(bad)

    def test_shape_rejects_nonfinite_and_bool(self):
        for value in (math.nan, math.inf, True, "1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                shape([[value]])

    def test_inner_dimension_mismatch(self):
        with self.assertRaises(ValueError):
            matmul([[1, 2]], [[1, 2]])

    def test_residual_shape_mismatch(self):
        with self.assertRaises(ValueError):
            add([[1, 2]], [[1]])

    def test_residual_numeric_addition(self):
        self.assertEqual(add([[1, -1]], [[2, 3]]), [[3, 2]])

    def test_linear_bias_is_shared_across_positions(self):
        self.assertEqual(linear([[1, 2], [3, 4]], identity(2), [2, -1]),
                         [[3, 1], [5, 3]])

    def test_linear_rejects_bias_width(self):
        with self.assertRaises(ValueError):
            linear([[1, 2]], identity(2), [1])


class AttentionTests(unittest.TestCase):
    def test_hand_computed_attention(self):
        out, weights, scores = scaled_attention(
            [[1, 0]], [[1, 0], [0, 1]], [[10, 0], [0, 20]])
        expected = math.exp(1 / math.sqrt(2)) / (math.exp(1 / math.sqrt(2)) + 1)
        self.assertAlmostEqual(scores[0][0], 1 / math.sqrt(2))
        self.assertAlmostEqual(weights[0][0], expected)
        self.assertAlmostEqual(weights[0][1], 1 - expected)
        self.assertAlmostEqual(out[0][0], 10 * expected)
        self.assertAlmostEqual(out[0][1], 20 * (1 - expected))

    def test_zero_query_gives_uniform_weights(self):
        out, weights, _ = scaled_attention([[0, 0]], [[3, 4], [-7, 9]],
                                            [[2], [8]])
        self.assertEqual(weights, [[0.5, 0.5]])
        self.assertEqual(out, [[5]])

    def test_qk_width_and_value_width_need_not_match(self):
        out, weights, _ = scaled_attention([[1, 0], [0, 1]],
                                            [[1, 0], [0, 1], [1, 1]],
                                            [[1], [2], [3]])
        self.assertEqual(shape(out), (2, 1))
        self.assertEqual(shape(weights), (2, 3))

    def test_attention_weights_normalize_per_query(self):
        _, weights, _ = scaled_attention([[2, -1], [0, 3]],
                                          [[2, 0], [0, 2], [1, 1]],
                                          [[1], [2], [3]])
        for row in weights:
            self.assertAlmostEqual(sum(row), 1)
            self.assertTrue(all(0 <= value <= 1 for value in row))

    def test_causal_future_weights_are_zero(self):
        x = [[1, 0], [0, 1], [1, 1]]
        out, weights, _ = scaled_attention(x, x, x, causal_allowed(3))
        self.assertEqual(weights[0], [1, 0, 0])
        self.assertEqual(weights[1][2], 0)
        self.assertEqual(out[0], x[0])

    def test_future_value_changes_do_not_affect_prefix(self):
        qk = [[1, 0], [0, 1], [1, 1]]
        a, _, _ = scaled_attention(qk, qk, [[1], [2], [3]], causal_allowed(3))
        b, _, _ = scaled_attention(qk, qk, [[1], [2], [300]], causal_allowed(3))
        self.assertEqual(a[:2], b[:2])
        self.assertNotEqual(a[2], b[2])

    def test_stable_softmax_large_logits(self):
        weights = stable_softmax([1000, 999])
        self.assertAlmostEqual(weights[0], 1 / (1 + math.exp(-1)))
        self.assertAlmostEqual(sum(weights), 1)

    def test_all_masked_row_is_explicit_error(self):
        with self.assertRaises(ValueError):
            scaled_attention([[1]], [[1]], [[2]], [[False]])

    def test_rejects_mask_shape_and_non_bool(self):
        for bad in ([[True, False]], [[1]], []):
            with self.subTest(mask=bad), self.assertRaises(ValueError):
                scaled_attention([[1]], [[1]], [[2]], bad)

    def test_rejects_qk_and_kv_mismatch(self):
        with self.assertRaises(ValueError):
            scaled_attention([[1]], [[1, 2]], [[3]])
        with self.assertRaises(ValueError):
            scaled_attention([[1]], [[1], [2]], [[3]])

    def test_causal_mask_rejects_invalid_length(self):
        for bad in (0, -1, 2.5, True):
            with self.subTest(length=bad), self.assertRaises(ValueError):
                causal_allowed(bad)


class MultiheadTests(unittest.TestCase):
    def test_two_positions_have_distinct_numeric_head_results(self):
        x = [[1, 0, 2, 0], [0, 1, 0, 1]]
        out, trace = multihead_self_attention(x, *(identity(4) for _ in range(4)), 2)
        p = math.exp(1 / math.sqrt(2)) / (math.exp(1 / math.sqrt(2)) + 1)
        p2 = math.exp(4 / math.sqrt(2)) / (math.exp(4 / math.sqrt(2)) + 1)
        expected_weights = [[[p, 1 - p], [1 - p, p]],
                            [[p2, 1 - p2], [1 - p, p]]]
        expected_output = [[p, 1 - p, 2 * p2, 1 - p2],
                           [1 - p, p, 2 * (1 - p), p]]
        for actual_head, expected_head in zip(trace["head_weights"], expected_weights):
            for actual_row, expected_row in zip(actual_head, expected_head):
                for actual, expected in zip(actual_row, expected_row):
                    self.assertAlmostEqual(actual, expected)
        for actual_row, expected_row in zip(out, expected_output):
            for actual, expected in zip(actual_row, expected_row):
                self.assertAlmostEqual(actual, expected)

    def test_multihead_honors_mask_and_future_input_isolation(self):
        x = [[1, 0, 2, 0], [0, 1, 0, 1]]
        changed = [[1, 0, 2, 0], [9, 7, 11, 3]]
        mask = causal_allowed(2)
        a, trace = multihead_self_attention(x, *(identity(4) for _ in range(4)), 2, mask)
        b, _ = multihead_self_attention(changed, *(identity(4) for _ in range(4)), 2, mask)
        self.assertEqual(a[0], x[0])
        self.assertEqual(a[0], b[0])
        self.assertNotEqual(a[1], b[1])
        for head in trace["head_weights"]:
            self.assertEqual(head[0], [1, 0])

    def test_concatenates_instead_of_adding_heads(self):
        x = [[1, 2, 3, 4]]
        out, trace = multihead_self_attention(x, *(identity(4) for _ in range(4)), 2)
        self.assertEqual(trace["concatenated"], x)
        self.assertEqual(out, x)
        self.assertEqual(len(trace["head_weights"]), 2)

    def test_output_projection_mixes_head_features(self):
        x = [[1, 2, 3, 4]]
        wo = [[1, 0, 0, 0], [0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1]]
        out, trace = multihead_self_attention(x, identity(4), identity(4),
                                              identity(4), wo, 2)
        self.assertEqual(trace["concatenated"], [[1, 2, 3, 4]])
        self.assertEqual(out, [[4, 6, 3, 4]])

    def test_separate_qk_projections_change_attention(self):
        x = [[1, 0], [0, 1]]
        _, base = multihead_self_attention(x, identity(2), identity(2),
                                           identity(2), identity(2), 1)
        _, swapped = multihead_self_attention(x, identity(2), [[0, 1], [1, 0]],
                                              identity(2), identity(2), 1)
        self.assertGreater(base["head_weights"][0][0][0], 0.5)
        self.assertLess(swapped["head_weights"][0][0][0], 0.5)

    def test_head_count_and_projection_shape_errors(self):
        for heads in (0, 3, True):
            with self.subTest(heads=heads), self.assertRaises(ValueError):
                multihead_self_attention([[1, 2]], *(identity(2) for _ in range(4)), heads)
        with self.assertRaises(ValueError):
            multihead_self_attention([[1, 2]], identity(1), identity(2),
                                      identity(2), identity(2), 1)

    def test_does_not_mutate_inputs(self):
        x, w, mask = [[1, 2], [3, 4]], identity(2), causal_allowed(2)
        originals = copy.deepcopy((x, w, mask))
        multihead_self_attention(x, w, w, w, w, 2, mask)
        self.assertEqual((x, w, mask), originals)


class FFNAndNormTests(unittest.TestCase):
    def test_ffn_nonzero_hidden_bias_changes_relu_gate(self):
        out = feed_forward([[-2, 3]], identity(2), [3, -4], identity(2), [2, 5])
        # Hidden before ReLU [1,-1], after ReLU [1,0], output [3,5].
        self.assertEqual(out, [[3, 5]])

    def test_pre_ln_nonzero_branch_inputs_and_order(self):
        calls = []
        def attention(x):
            calls.append(("attention", copy.deepcopy(x)))
            return [[2, -1]]
        def ffn(x):
            calls.append(("ffn", copy.deepcopy(x)))
            return [[1, 2]]
        out = transformer_block([[1, 3]], attention, ffn, True)
        self.assertEqual([name for name, _ in calls], ["attention", "ffn"])
        self.assertAlmostEqual(calls[0][1][0][0], -1 / math.sqrt(1 + 1e-5))
        self.assertAlmostEqual(calls[0][1][0][1], 1 / math.sqrt(1 + 1e-5))
        # middle = [1,3] + [2,-1] = [3,2], not the original x.
        self.assertAlmostEqual(calls[1][1][0][0], 0.5 / math.sqrt(0.25 + 1e-5))
        self.assertAlmostEqual(calls[1][1][0][1], -0.5 / math.sqrt(0.25 + 1e-5))
        self.assertEqual(out, [[4, 4]])

    def test_post_ln_nonzero_branch_inputs_and_order(self):
        calls = []
        def attention(x):
            calls.append(("attention", copy.deepcopy(x)))
            return [[2, -1]]
        def ffn(x):
            calls.append(("ffn", copy.deepcopy(x)))
            return [[1, 2]]
        out = transformer_block([[1, 3]], attention, ffn, False)
        self.assertEqual([name for name, _ in calls], ["attention", "ffn"])
        self.assertEqual(calls[0][1], [[1, 3]])
        middle_first = 0.5 / math.sqrt(0.25 + 1e-5)
        self.assertAlmostEqual(calls[1][1][0][0], middle_first)
        self.assertAlmostEqual(calls[1][1][0][1], -middle_first)
        # The final LN input is [middle_first+1, -middle_first+2].
        centered = middle_first - 0.5
        expected = centered / math.sqrt(centered ** 2 + 1e-5)
        self.assertAlmostEqual(out[0][0], expected)
        self.assertAlmostEqual(out[0][1], -expected)

    def test_ffn_relu_and_dimension_changes(self):
        out = feed_forward([[-2, 3]], [[1, 0, 1], [0, 1, 1]], [0, 0, 0],
                           [[1, 0], [0, 1], [1, 1]], [0, 0])
        self.assertEqual(out, [[1, 4]])

    def test_ffn_does_not_mix_positions(self):
        f = lambda x: feed_forward(x, identity(2), [0, 0], identity(2), [1, 1])
        a = f([[2, -1], [5, 4]])
        b = f([[2, -1], [-999, 999]])
        self.assertEqual(a[0], b[0])
        self.assertNotEqual(a[1], b[1])

    def test_ffn_requires_residual_output_width(self):
        with self.assertRaises(ValueError):
            feed_forward([[1, 2]], identity(2), [0, 0], [[1], [1]], [0])

    def test_layer_norm_population_variance(self):
        out = layer_norm([[1, 3]], eps=1e-5)
        self.assertAlmostEqual(out[0][0], -1 / math.sqrt(1 + 1e-5))
        self.assertAlmostEqual(out[0][1], 1 / math.sqrt(1 + 1e-5))

    def test_layer_norm_does_not_mix_positions(self):
        a = layer_norm([[1, 3], [5, 9]])
        b = layer_norm([[1, 3], [-100, 100]])
        self.assertEqual(a[0], b[0])

    def test_constant_row_and_affine_parameters(self):
        self.assertEqual(layer_norm([[7, 7]], [2, 3], [4, 5]), [[4, 5]])
        out = layer_norm([[1, 3]], [2, 3], [4, 5])
        self.assertAlmostEqual(out[0][0], 4 - 2 / math.sqrt(1 + 1e-5))
        self.assertAlmostEqual(out[0][1], 5 + 3 / math.sqrt(1 + 1e-5))

    def test_rejects_norm_parameters(self):
        for eps in (0, -1, math.inf, True):
            with self.subTest(eps=eps), self.assertRaises(ValueError):
                layer_norm([[1, 3]], eps=eps)
        with self.assertRaises(ValueError):
            layer_norm([[1, 3]], gamma=[1])

    def test_zero_branches_pre_ln_preserves_identity(self):
        zeros = lambda x: [[0] * len(row) for row in x]
        x = [[1, 3]]
        self.assertEqual(transformer_block(x, zeros, zeros, True), x)
        self.assertNotEqual(transformer_block(x, zeros, zeros, False), x)

    def test_residual_branch_shape_is_checked(self):
        with self.assertRaises(ValueError):
            transformer_block([[1, 3]], lambda _: [[0]], lambda x: x)

    def test_demo_shapes_finiteness_and_determinism(self):
        result = demo()
        self.assertEqual(result, demo())
        self.assertEqual(result["head_weights_shape"], [2, 3, 3])
        self.assertEqual(len(result["head_weights"]), 2)
        for head in result["head_weights"]:
            self.assertEqual(shape(head), (3, 3))
        self.assertEqual(result["concatenated_shape"], [3, 4])
        for name in ("mha_output", "pre_ln_output", "post_ln_output"):
            self.assertEqual(shape(result[name]), (3, 4))


if __name__ == "__main__":
    unittest.main(verbosity=2)
