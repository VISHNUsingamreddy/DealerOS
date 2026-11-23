import csv, os
from django.core.management.base import BaseCommand
from django.conf import settings
from reconcile.models import Location, SystemARecord, SystemBEntry
from reconcile.cleaning import normalize_ref, parse_amount, parse_date
class Command(BaseCommand):
    help='Import locations/system_a/system_b CSVs. Idempotent via update_or_create.'
    def handle(self,*a,**o):
        base=os.path.join(settings.BASE_DIR,'data')
        def rows(name):
            with open(os.path.join(base,name),newline='',encoding='utf-8-sig') as f:
                return list(csv.DictReader(f))
        locs=rows('locations.csv')
        for r in locs:
            Location.objects.update_or_create(location_id=r['location_id'].strip(),defaults={'org_id':r['org_id'].strip(),'name':(r.get('location_name') or '').strip()})
        locmap={l.location_id:l for l in Location.objects.all()}
        a_rows=rows('system_a.csv'); saved_a=0
        for r in a_rows:
            actor=(r.get('actor_id') or '').strip() or None
            SystemARecord.objects.update_or_create(record_id=r['record_id'].strip(),defaults={
                'location':locmap[r['location_id'].strip()],'event_date':parse_date(r['event_date']),
                'category_code':(r.get('category_code') or '').strip(),'actor_id':actor,
                'base_value':parse_amount(r['base_value']),'adjustment':parse_amount(r['adjustment']),
                'total_value':parse_amount(r['total_value']),'state':(r.get('state') or '').strip()})
            saved_a+=1
        b_rows=rows('system_b.csv'); saved_b=0; blank=0; cleaned=0
        for r in b_rows:
            raw=(r.get('record_ref') or '')
            norm=normalize_ref(raw)
            if raw.strip()!=norm: cleaned+=1
            val=parse_amount(r.get('value'))
            if (r.get('value') or '').strip()=='': blank+=1
            SystemBEntry.objects.update_or_create(entry_id=r['entry_id'].strip(),defaults={
                'record_ref_raw':raw,'record_ref':norm,'location':locmap[r['location_id'].strip()],
                'recorded_on':parse_date(r['recorded_on']),'value_raw':(r.get('value') or ''),
                'value':val,'label':(r.get('label') or '').strip()})
            saved_b+=1
        self.stdout.write(f"A: {len(a_rows)} read, {saved_a} saved; B: {len(b_rows)} read, {saved_b} saved; values left empty: {blank}; refs cleaned: {cleaned}")
