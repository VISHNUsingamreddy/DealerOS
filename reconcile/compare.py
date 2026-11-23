from decimal import Decimal
# Pure function: no DB, no web code. a_rows: {record_id: dict(total,location,date,state,org)}
# b_rows: list of dict(entry_id,ref,value,location,date,org). Returns list of dicts.
def compare(a_rows, b_rows):
    out=[]; by_ref={}
    for e in b_rows: by_ref.setdefault(e["ref"],[]).append(e)
    for ref, entries in by_ref.items():
        if ref not in a_rows:
            for e in entries:
                out.append({"reason":"ORPHAN_IN_B","record_id":ref,"entry_id":e["entry_id"],
                    "a_location":None,"b_location":e["location"],"a_value":None,"b_value":e["value"],
                    "org":e["org"],"cross_org":False})
    for rid, a in a_rows.items():
        entries=by_ref.get(rid,[])
        if not entries:
            out.append({"reason":"MISSING_IN_B","record_id":rid,"entry_id":None,
                "a_location":a["location"],"b_location":None,"a_value":a["total"],"b_value":None,
                "org":a["org"],"cross_org":False}); continue
        # VOIDED: a B entry should not stand for a voided record.
        if a.get("state")=="VOIDED":
            e=entries[0]
            out.append({"reason":"VOIDED_WITH_B_ENTRY","record_id":rid,"entry_id":e["entry_id"],
                "a_location":a["location"],"b_location":e["location"],"a_value":a["total"],"b_value":e["value"],
                "org":a["org"],"cross_org":e["org"]!=a["org"]}); continue
        vals=[e["value"] for e in entries]
        if any(v is None for v in vals):
            out.append({"reason":"VALUE_MISMATCH","record_id":rid,"entry_id":entries[0]["entry_id"],
                "a_location":a["location"],"b_location":entries[0]["location"],"a_value":a["total"],
                "b_value":vals[0] if len(vals)==1 else None,"org":a["org"],
                "cross_org":any(e["org"]!=a["org"] for e in entries)}); continue
        if len(entries)>1:
            if sum(vals)!=a["total"]:  # split that sums exactly is fine
                out.append({"reason":"DUPLICATE_IN_B","record_id":rid,"entry_id":entries[0]["entry_id"],
                    "a_location":a["location"],"b_location":entries[0]["location"],"a_value":a["total"],
                    "b_value":sum(vals),"org":a["org"],"cross_org":any(e["org"]!=a["org"] for e in entries)})
            continue
        e=entries[0]
        if e["value"]!=a["total"]:
            out.append({"reason":"VALUE_MISMATCH","record_id":rid,"entry_id":e["entry_id"],
                "a_location":a["location"],"b_location":e["location"],"a_value":a["total"],"b_value":e["value"],
                "org":a["org"],"cross_org":e["org"]!=a["org"]})
        if e["location"]!=a["location"]:
            out.append({"reason":"LOCATION_MISMATCH","record_id":rid,"entry_id":e["entry_id"],
                "a_location":a["location"],"b_location":e["location"],"a_value":a["total"],"b_value":e["value"],
                "org":a["org"],"cross_org":e["org"]!=a["org"]})
        if e["date"]!=a["date"]:
            out.append({"reason":"DATE_MISMATCH","record_id":rid,"entry_id":e["entry_id"],
                "a_location":a["location"],"b_location":e["location"],"a_value":a["total"],"b_value":e["value"],
                "org":a["org"],"cross_org":e["org"]!=a["org"]})
    return out
