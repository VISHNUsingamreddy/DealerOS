from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Q
from .models import SystemARecord, SystemBEntry
from .compare import compare
REASONS=['MISSING_IN_B','ORPHAN_IN_B','DUPLICATE_IN_B','VALUE_MISMATCH','LOCATION_MISMATCH','DATE_MISMATCH','VOIDED_WITH_B_ENTRY']
def _disagreements(org, reason=None, sort=None):
    # Tenant filter is in the DB query: only rows whose owning org == org are loaded.
    a_qs=SystemARecord.objects.select_related('location').filter(location__org_id=org)
    # B entries for those A records + orphans owned by this org. Orphans have no A row.
    a_ids=set(a_qs.values_list('record_id',flat=True))
    all_a_ids=set(SystemARecord.objects.values_list('record_id',flat=True))
    # A B entry belongs here if it matches one of MY A records, OR it is a true orphan
    # (ref in NO A record at all) owned by my org. A cross-org entry like REC-1077's B side
    # matches an A record owned by the OTHER org, so it must NOT appear as an orphan here.
    b_qs=SystemBEntry.objects.select_related('location').filter(Q(record_ref__in=a_ids)| (Q(location__org_id=org) & ~Q(record_ref__in=all_a_ids)))
    a_rows={r.record_id:{'total':r.total_value,'location':r.location.location_id,'date':r.event_date,'state':r.state,'org':r.location.org_id} for r in a_qs}
    b_rows=[{'entry_id':e.entry_id,'ref':e.record_ref,'value':e.value,'location':e.location.location_id,'date':e.recorded_on,'org':e.location.org_id} for e in b_qs]
    out=compare(a_rows,b_rows)
    out=[r for r in out if r['org']==org]  # defence in depth; compare already scoped
    # Cross-org: hide the other org's location. Never leak LOC-201 to ORG-A etc.
    for r in out:
        if r.get('cross_org'): r['b_location']=None
    if reason in REASONS: out=[r for r in out if r['reason']==reason]
    # Sorting: value = B value if present else A value; None last.
    def key(r):
        v=r['b_value'] if r['b_value'] is not None else r['a_value']
        return (v is None, v)
    if sort=='-value': out=sorted(out,key=key,reverse=True)
    elif sort=='value': out=sorted(out,key=key)
    # Serialise Decimals, compute difference
    res=[]
    for r in out:
        av=r['a_value']; bv=r['b_value']
        diff=(bv-av) if (av is not None and bv is not None) else None
        res.append({'reason':r['reason'],'record_id':r['record_id'],'location':r['a_location'] or r['b_location'],
            'a_location':r['a_location'],'b_location':r['b_location'],
            'a_value':str(av) if av is not None else None,'b_value':str(bv) if bv is not None else None,
            'difference':str(diff) if diff is not None else None})
    return res
def disagreements_api(request):
    org=request.GET.get('org')
    if org not in ('ORG-A','ORG-B'): return JsonResponse({'error':'?org=ORG-A or ORG-B is required'},status=400)
    return JsonResponse(_disagreements(org,request.GET.get('reason'),request.GET.get('sort')),safe=False)
def index(request):
    org=request.GET.get('org','ORG-A'); reason=request.GET.get('reason',''); sort=request.GET.get('sort','')
    rows=_disagreements(org,reason or None,sort or None)
    return render(request,'reconcile/index.html',{'rows':rows,'org':org,'reason':reason,'sort':sort,'reasons':REASONS})
