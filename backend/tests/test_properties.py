BASE = "/api/v1/properties"

RENTAL = {
    "kind": "rental",
    "nickname": "Maple St duplex",
    "city": "Atlanta",
    "state": "GA",
    "purchase_price": "300000.00",
    "purchase_date": "2024-03-01",
    "down_payment": "60000.00",
}


def test_create_returns_baseline_valuation(client):
    res = client.post(BASE, json=RENTAL)
    assert res.status_code == 201
    body = res.json()
    assert body["nickname"] == "Maple St duplex"
    assert body["latest_value"] == "300000.00"
    assert body["latest_value_source"] == "purchase_price"

    vals = client.get(f"{BASE}/{body['id']}/valuations").json()
    assert len(vals) == 1
    assert vals[0]["source"] == "purchase_price"


def test_create_without_purchase_has_no_valuation(client):
    res = client.post(BASE, json={"kind": "other", "nickname": "Mystery shack"})
    assert res.status_code == 201
    assert res.json()["latest_value"] is None


def test_list_and_kind_filter(client):
    client.post(BASE, json=RENTAL)
    client.post(BASE, json={"kind": "airbnb", "nickname": "Lake cabin"})
    assert len(client.get(BASE).json()) == 2
    rentals = client.get(BASE, params={"kind": "rental"}).json()
    assert [p["nickname"] for p in rentals] == ["Maple St duplex"]


def test_only_one_my_home(client):
    assert client.post(BASE, json={"kind": "my_home", "nickname": "Home"}).status_code == 201
    res = client.post(BASE, json={"kind": "my_home", "nickname": "Home 2"})
    assert res.status_code == 409


def test_patch_updates_fields(client):
    pid = client.post(BASE, json=RENTAL).json()["id"]
    res = client.patch(f"{BASE}/{pid}", json={"nickname": "Maple St", "beds": 3})
    assert res.status_code == 200
    assert res.json()["nickname"] == "Maple St"
    assert res.json()["beds"] == 3


def test_delete_cascades(client):
    pid = client.post(BASE, json=RENTAL).json()["id"]
    assert client.delete(f"{BASE}/{pid}").status_code == 204
    assert client.get(f"{BASE}/{pid}").status_code == 404


def test_manual_valuation_becomes_latest(client):
    pid = client.post(BASE, json=RENTAL).json()["id"]
    res = client.post(
        f"{BASE}/{pid}/valuations",
        json={"value": "325000.00", "valued_at": "2025-06-01", "note": "appraisal"},
    )
    assert res.status_code == 201
    assert res.json()["source"] == "manual"
    prop = client.get(f"{BASE}/{pid}").json()
    assert prop["latest_value"] == "325000.00"
    assert prop["latest_value_source"] == "manual"


def test_other_users_cannot_see_property(client, as_other_user):
    pid = client.post(BASE, json=RENTAL).json()["id"]
    as_other_user()
    assert client.get(f"{BASE}/{pid}").status_code == 404
    assert client.get(BASE).json() == []
