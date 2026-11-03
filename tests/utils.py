
def parse_product(*, response, schema):
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")

    payload = response.json()

    parsed = schema.model_validate(payload)

    return parsed

def parse_error_detail(*, payload, response):
    assert payload["error"] is True
    assert payload["status_code"] == response.status_code
    assert "detail" in payload

    detail = payload["detail"]

    return detail