from app.services.policy_engine import path_matches


def test_dynamic_order_id_path_matching() -> None:
    pattern = "/api/orders/{order_id}/cancel"

    assert path_matches(pattern, "/api/orders/123/cancel")
    assert path_matches(pattern, "/api/orders/abc-uuid/cancel")
    assert not path_matches(pattern, "/api/orders/cancel-all")
    assert not path_matches(pattern, "/api/orders/123/refund")
    assert not path_matches(pattern, "/api/orders/123/cancel/extra")


def test_get_order_pattern_does_not_match_collection() -> None:
    assert path_matches("/api/orders/{order_id}", "/api/orders/123")
    assert not path_matches("/api/orders/{order_id}", "/api/orders")
    assert path_matches("/api/orders", "/api/orders")
