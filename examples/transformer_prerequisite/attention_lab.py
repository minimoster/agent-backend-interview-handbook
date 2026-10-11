"""Small, untrained Transformer forward-pass lab using only the Python stdlib.

Matrices are lists of rows: [sequence, feature]. There is no batch axis,
autograd, dropout, tokenizer, vocabulary head, model download, or GPU work.
Mask convention: True means ALLOWED, not blocked. Do not copy this convention
blindly into a framework API. Weights below are handcrafted teaching inputs.
"""

import json
import math


def shape(matrix):
    """Validate a nonempty rectangular finite numeric matrix."""
    if not isinstance(matrix, list) or not matrix:
        raise ValueError("matrix must be a nonempty list of rows")
    if not all(isinstance(row, list) and row for row in matrix):
        raise ValueError("rows must be nonempty lists")
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("matrix must be rectangular")
    if any(isinstance(v, bool) or not isinstance(v, (int, float))
           or not math.isfinite(v) for row in matrix for v in row):
        raise ValueError("matrix values must be finite numbers")
    return len(matrix), width


def matmul(a, b):
    rows, inner = shape(a)
    b_rows, cols = shape(b)
    if inner != b_rows:
        raise ValueError("matrix inner dimensions must agree")
    return [[sum(a[i][k] * b[k][j] for k in range(inner))
             for j in range(cols)] for i in range(rows)]


def add(a, b):
    if shape(a) != shape(b):
        raise ValueError("residual addition needs identical shapes")
    return [[u + v for u, v in zip(arow, brow)]
            for arow, brow in zip(a, b)]


def linear(x, weight, bias=None):
    """Row-vector convention: x @ weight + bias, unlike nn.Linear storage."""
    out = matmul(x, weight)
    width = len(out[0])
    if bias is None:
        bias = [0.0] * width
    if not isinstance(bias, list) or len(bias) != width:
        raise ValueError("bias width must match output width")
    shape([bias])
    return [[v + b for v, b in zip(row, bias)] for row in out]


def stable_softmax(scores, allowed=None):
    """Normalize one query's scores across keys; masked positions are zero."""
    shape([scores])
    if allowed is None:
        allowed = [True] * len(scores)
    if (not isinstance(allowed, list) or len(allowed) != len(scores)
            or any(type(v) is not bool for v in allowed)):
        raise ValueError("allowed must contain one bool per key")
    if not any(allowed):
        raise ValueError("all keys masked: this lab refuses undefined softmax")
    maximum = max(v for v, keep in zip(scores, allowed) if keep)
    exps = [math.exp(v - maximum) if keep else 0.0
            for v, keep in zip(scores, allowed)]
    total = sum(exps)
    return [v / total for v in exps]


def causal_allowed(length):
    """Square self-attention mask. Row i can read keys 0 through i."""
    if type(length) is not int or length <= 0:
        raise ValueError("length must be a positive integer")
    return [[j <= i for j in range(length)] for i in range(length)]


def scaled_attention(q, k, v, allowed=None):
    """Return (output, weights, scores) with shapes Lq×dv, Lq×Lk, Lq×Lk."""
    lq, dk = shape(q)
    lk, key_dim = shape(k)
    lv, _ = shape(v)
    if dk != key_dim or lk != lv:
        raise ValueError("Q/K widths and K/V sequence lengths must agree")
    if allowed is None:
        allowed = [[True] * lk for _ in range(lq)]
    if (not isinstance(allowed, list) or len(allowed) != lq
            or any(not isinstance(row, list) or len(row) != lk
                   or any(type(value) is not bool for value in row)
                   for row in allowed)):
        raise ValueError("allowed mask must have shape Lq×Lk and bool entries")
    kt = [list(column) for column in zip(*k)]
    scores = [[value / math.sqrt(dk) for value in row]
              for row in matmul(q, kt)]
    weights = [stable_softmax(row, mask)
               for row, mask in zip(scores, allowed)]
    return matmul(weights, v), weights, scores


def multihead_self_attention(x, wq, wk, wv, wo, heads, allowed=None):
    """Equal-width MHA for teaching: learned projections, split, concat, W^O.

    This restricted lab requires all four projections to be d_model×d_model.
    The general attention formula does not require d_k == d_v.
    """
    _, d_model = shape(x)
    if type(heads) is not int or heads <= 0 or d_model % heads:
        raise ValueError("positive heads must divide d_model in this lab")
    for weight in (wq, wk, wv, wo):
        if shape(weight) != (d_model, d_model):
            raise ValueError("this lab needs square d_model projections")
    q, k, v = linear(x, wq), linear(x, wk), linear(x, wv)
    head_dim = d_model // heads
    head_outputs, head_weights = [], []
    for head in range(heads):
        start, stop = head * head_dim, (head + 1) * head_dim
        qh, kh, vh = ([[row[j] for j in range(start, stop)] for row in m]
                      for m in (q, k, v))
        out, weights, _ = scaled_attention(qh, kh, vh, allowed)
        head_outputs.append(out)
        head_weights.append(weights)
    concatenated = [[value for head in head_outputs for value in head[i]]
                    for i in range(len(x))]
    output = linear(concatenated, wo)
    return output, {"q": q, "k": k, "v": v,
                    "head_weights": head_weights,
                    "concatenated": concatenated}


def feed_forward(x, w1, b1, w2, b2):
    """Same two linear transforms and ReLU independently at every position."""
    _, width = shape(x)
    if shape(w1)[0] != width or shape(w2) != (shape(w1)[1], width):
        raise ValueError("FFN must map d_model→d_ff→d_model")
    hidden = [[max(0.0, v) for v in row] for row in linear(x, w1, b1)]
    return linear(hidden, w2, b2)


def layer_norm(x, gamma=None, beta=None, eps=1e-5):
    """Normalize each row across features, using population variance."""
    _, width = shape(x)
    if isinstance(eps, bool) or not isinstance(eps, (int, float)) \
            or not math.isfinite(eps) or eps <= 0:
        raise ValueError("eps must be finite and positive")
    gamma = [1.0] * width if gamma is None else gamma
    beta = [0.0] * width if beta is None else beta
    if not isinstance(gamma, list) or not isinstance(beta, list) \
            or len(gamma) != width or len(beta) != width:
        raise ValueError("gamma/beta width must match d_model")
    shape([gamma])
    shape([beta])
    out = []
    for row in x:
        mean = sum(row) / width
        variance = sum((v - mean) ** 2 for v in row) / width
        denominator = math.sqrt(variance + eps)
        out.append([(v - mean) / denominator * g + b
                    for v, g, b in zip(row, gamma, beta)])
    return out


def transformer_block(x, attention_fn, ffn_fn, norm_first=False):
    """One self-attention + FFN block, no dropout, default gamma=1/beta=0.

    Each LayerNorm uses separate *conceptual* parameters; this forward-only
    function supplies the same default values, not shared trained parameters.
    """
    if type(norm_first) is not bool:
        raise ValueError("norm_first must be bool")
    shape(x)
    if norm_first:
        middle = add(x, attention_fn(layer_norm(x)))
        return add(middle, ffn_fn(layer_norm(middle)))
    middle = layer_norm(add(x, attention_fn(x)))
    return layer_norm(add(middle, ffn_fn(middle)))


def identity(width):
    if type(width) is not int or width <= 0:
        raise ValueError("width must be a positive integer")
    return [[float(i == j) for j in range(width)] for i in range(width)]


def demo():
    # Original hand example: one query and two keys; separate tests cover dv!=dk.
    out, weights, scores = scaled_attention(
        [[1.0, 0.0]], [[1.0, 0.0], [0.0, 1.0]],
        [[10.0, 0.0], [0.0, 20.0]])
    # Three positions with d_model=4, h=2. Identity projections are deliberately
    # simplistic teaching weights, not learned semantic embeddings.
    x = [[1.0, 0.0, 1.0, 0.0], [0.0, 1.0, 0.0, 1.0],
         [1.0, 1.0, 0.0, 1.0]]
    wq = identity(4)
    wk = [[0.0, 1.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0],
          [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
    wv = identity(4)
    wo = [[1.0, 0.0, 0.5, 0.0], [0.0, 1.0, 0.0, 0.5],
          [0.5, 0.0, 1.0, 0.0], [0.0, 0.5, 0.0, 1.0]]
    allowed = causal_allowed(3)
    attention = lambda z: multihead_self_attention(
        z, wq, wk, wv, wo, 2, allowed)[0]
    # d_ff=6, including some negative inputs to expose the ReLU step.
    w1 = [[1, 0, 0, 0, 1, -1], [0, 1, 0, 0, 1, 0],
          [0, 0, 1, 0, 0, 1], [0, 0, 0, 1, -1, 1]]
    w2 = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0],
          [0, 0, 0, 1], [0.2, 0.2, 0, 0], [0, 0, 0.2, 0.2]]
    ffn = lambda z: feed_forward(z, w1, [0.0] * 6, w2, [0.0] * 4)
    mha_out, trace = multihead_self_attention(x, wq, wk, wv, wo, 2, allowed)
    return {"scope": "handcrafted CPU forward arithmetic; no training/GPU/model",
            "hand_scores": scores, "hand_weights": weights, "hand_output": out,
            "x_shape": list(shape(x)), "q_shape": list(shape(trace["q"])),
            "head_weights_shape": [len(trace["head_weights"]),
                                   *shape(trace["head_weights"][0])],
            "head_weights": trace["head_weights"],
            "concatenated_shape": list(shape(trace["concatenated"])),
            "mha_output_shape": list(shape(mha_out)),
            "mha_output": mha_out,
            "post_ln_output": transformer_block(x, attention, ffn),
            "pre_ln_output": transformer_block(x, attention, ffn, True)}


if __name__ == "__main__":
    print(json.dumps(demo(), ensure_ascii=False, indent=2))
