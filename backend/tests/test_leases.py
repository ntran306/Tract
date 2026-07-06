PROPS = "/api/v1/properties"

LEASE = {
    "tenant_name": "Jordan Doe",
    "rent": "1800.00",
    "start_date": "2026-01-01",
}


def test_lease_lifecycle(client):
    pid = client.post(PROPS, json={"kind": "rental", "nickname": "Maple St"}).json()["id"]

    assert client.get(f"{PROPS}/{pid}/lease").status_code == 404

    res = client.put(f"{PROPS}/{pid}/lease", json=LEASE)
    assert res.status_code == 200
    assert res.json()["tenant_name"] == "Jordan Doe"

    # upsert updates in place, not duplicates
    res = client.put(f"{PROPS}/{pid}/lease", json={**LEASE, "rent": "1900.00"})
    assert res.json()["rent"] == "1900.00"

    assert client.delete(f"{PROPS}/{pid}/lease").status_code == 204
    assert client.get(f"{PROPS}/{pid}/lease").status_code == 404


def test_lease_rejected_for_non_rental(client):
    pid = client.post(PROPS, json={"kind": "airbnb", "nickname": "Cabin"}).json()["id"]
    assert client.put(f"{PROPS}/{pid}/lease", json=LEASE).status_code == 400
