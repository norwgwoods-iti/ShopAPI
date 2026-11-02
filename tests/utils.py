
def parse_product(*, response, schema):
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/json")

    payload = response.json()

    parse = schema.model_validate(payload)

    return parse

def http_except_error_detail(*, payload, response):
    assert payload["error"] == True
    assert payload["status_code"] == response.status_code
    assert "detail" in payload

    detail = payload["detail"]

    return detail