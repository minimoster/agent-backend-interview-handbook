"""Original arithmetic model; not GPU measurement or a model implementation."""

def kv_bytes(*, batch: int, tokens: int, layers: int, kv_heads: int,
             head_dim: int, bytes_per_element: int) -> int:
    values = (batch, tokens, layers, kv_heads, head_dim, bytes_per_element)
    if any(type(x) is not int or x <= 0 for x in values):
        raise ValueError("all dimensions must be positive integers")
    return 2 * batch * tokens * layers * kv_heads * head_dim * bytes_per_element

if __name__ == "__main__":
    budget = kv_bytes(batch=1, tokens=4096, layers=32, kv_heads=8,
                      head_dim=128, bytes_per_element=2)
    print({"bytes": budget, "GiB": budget / 2**30})
