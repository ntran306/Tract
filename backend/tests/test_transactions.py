BASE = "/api/v1/transactions"
PROPS = "/api/v1/properties"


def make_property(client, **overrides):
    payload = {"kind": "rental", "nickname": "Maple St", **overrides}
    return client.post(PROPS, json=payload).json()["id"]


def make_txn(client, pid, **overrides):
    payload = {
        "property_id": pid,
        "kind": "income",
        "category": "rent",
        "amount": "1800.00",
        "occurred_on": "2026-06-01",
        **overrides,
    }
    return client.post(BASE, json=payload)


def test_create_and_list(client):
    pid = make_property(client)
    assert make_txn(client, pid).status_code == 201
    assert make_txn(
        client, pid, kind="expense", category="repairs", amount="240.50",
        occurred_on="2026-06-15", description="water heater",
    ).status_code == 201

    txns = client.get(BASE, params={"property_id": pid}).json()
    assert len(txns) == 2
    assert txns[0]["occurred_on"] == "2026-06-15"  # newest first


def test_category_must_match_kind(client):
    pid = make_property(client)
    res = make_txn(client, pid, kind="income", category="repairs")
    assert res.status_code == 422


def test_amount_must_be_positive(client):
    pid = make_property(client)
    assert make_txn(client, pid, amount="0").status_code == 422
    assert make_txn(client, pid, amount="-5").status_code == 422


def test_filters(client):
    pid = make_property(client)
    make_txn(client, pid)
    make_txn(client, pid, kind="expense", category="mortgage", occurred_on="2026-05-01")
    only_income = client.get(BASE, params={"kind": "income"}).json()
    assert len(only_income) == 1
    june = client.get(BASE, params={"date_from": "2026-06-01"}).json()
    assert len(june) == 1


def test_patch_revalidates_pairing(client):
    pid = make_property(client)
    tid = make_txn(client, pid).json()["id"]
    # changing kind alone would orphan the category -> rejected
    assert client.patch(f"{BASE}/{tid}", json={"kind": "expense"}).status_code == 422
    # changing both together is fine
    res = client.patch(f"{BASE}/{tid}", json={"kind": "expense", "category": "hoa"})
    assert res.status_code == 200


def test_cannot_post_to_foreign_property(client, as_other_user):
    pid = make_property(client)
    as_other_user()
    assert make_txn(client, pid).status_code == 404
    assert client.get(BASE).json() == []


def test_delete(client):
    pid = make_property(client)
    tid = make_txn(client, pid).json()["id"]
    assert client.delete(f"{BASE}/{tid}").status_code == 204
    assert client.get(BASE, params={"property_id": pid}).json() == []
