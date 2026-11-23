
from django.test import TestCase, Client
from django.core.management import call_command
from reconcile.models import SystemARecord, SystemBEntry
class TenantTest(TestCase):
    def test_tenant_isolation_and_counts(self):
        call_command("import_data")
        c=Client()
        a=c.get("/api/disagreements/?org=ORG-A").json()
        b=c.get("/api/disagreements/?org=ORG-B").json()
        assert not any(r.get("b_location") in ("LOC-201","LOC-202") for r in a), a
        assert not any(r.get("a_location") in ("LOC-101","LOC-102","LOC-103") for r in b), b
        assert any(r["record_id"]=="REC-1077" and r["reason"]=="LOCATION_MISMATCH" and r["b_location"] is None for r in a)
        assert not any(r["record_id"]=="REC-1077" for r in b)
        assert any(r["record_id"]=="REC-1999" for r in a) and not any(r["record_id"]=="REC-1999" for r in b)
        assert not any(r["record_id"]=="REC-1055" for r in a+b)
        assert any(r["record_id"]=="REC-1042" for r in a)
        assert SystemARecord.objects.count()==120 and SystemBEntry.objects.count()==121
        assert c.get("/api/disagreements/").status_code==400
