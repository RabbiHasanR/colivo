import re

import pytest
from fastapi.testclient import TestClient

from tests.conftest import FakeNotifier

PHONE = "01712 345678"
PHONE_E164 = "+8801712345678"


@pytest.mark.xfail(
    strict=True,
    reason="acceptance: an owner signs up, which creates their home, and is logged in",
)
def test_owner_signs_up_and_home_is_created(
    client: TestClient, notifier: FakeNotifier
) -> None:
    """
    GIVEN nobody uses the phone 01712 345678
    WHEN  its owner asks for a code and signs up with it, creating "Our Flat"
    THEN  they are logged in as the owner of Our Flat, which has a Home ID
          and a setup checklist with "Home created" done
    """
    client.post("/api/v1/auth/codes", json={"contact": PHONE})
    code = notifier.last_code_to(PHONE_E164)

    sign_up = client.post(
        "/api/v1/auth/sign-up",
        json={
            "contact": PHONE,
            "code": code,
            "name": "Rabbi Hasan",
            "home_name": "Our Flat",
            "area": "Mirpur",
            "first_month": "2026-11-01",
            "lives_here": True,
        },
    )
    me = client.get("/api/v1/me").json()["data"]
    setup = client.get("/api/v1/home/setup").json()["data"]

    assert sign_up.status_code == 201
    assert me["person"]["phone"] == PHONE_E164
    assert me["membership"]["name"] == "Rabbi Hasan"
    assert me["membership"]["role"] == "owner"
    assert me["home"]["name"] == "Our Flat"
    assert re.fullmatch(r"OF-\d{4}", me["home"]["code"])
    assert {"key": "home_created", "done": True} in setup["steps"]
