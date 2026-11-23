from decimal import Decimal
import pytest
from reconcile.compare import compare
from reconcile.cleaning import normalize_ref, parse_amount
def A(total='100.00',loc='L1',date='2026-03-01',state='CONFIRMED',org='ORG-A'):
    return {'total':Decimal(total),'location':loc,'date':date,'state':state,'org':org}
def B(eid='E1',ref='REC-1',val='100.00',loc='L1',date='2026-03-01',org='ORG-A'):
    return {'entry_id':eid,'ref':ref,'value':Decimal(val) if val is not None else None,'location':loc,'date':date,'org':org}
def test_missing(): assert compare({'REC-1':A()},{})[0]['reason']=='MISSING_IN_B'
def test_orphan(): assert compare({},[B(ref='REC-999')])[0]['reason']=='ORPHAN_IN_B'
def test_duplicate_same_amount_twice():
    out=compare({'REC-1':A()},[B(),B(eid='E2')]); assert [x['reason'] for x in out]==['DUPLICATE_IN_B']
def test_value_mismatch(): assert compare({'REC-1':A()},[B(val='90.00')])[0]['reason']=='VALUE_MISMATCH'
def test_blank_value_is_flagged_not_zero():
    out=compare({'REC-1':A()},[B(val=None)]); assert out[0]['reason']=='VALUE_MISMATCH' and out[0]['b_value'] is None
def test_split_that_sums_is_not_an_error():
    a={'REC-1':A()}; b=[B(val='40.00'),B(eid='E2',val='60.00')]; assert compare(a,b)==[]
def test_messy_refs_not_flagged():
    assert normalize_ref('rec1034')=='REC-1034' and normalize_ref(' REC - 1070 ')=='REC-1070' and normalize_ref('1112')=='REC-1112'
    assert parse_amount('1,25,400.00')==Decimal('125400.00') and parse_amount('') is None
def test_clean_row(): assert compare({'REC-1':A()},[B()])==[]
def test_location_mismatch(): assert compare({'REC-1':A()},[B(loc='L2')])[0]['reason']=='LOCATION_MISMATCH'
def test_date_mismatch(): assert compare({'REC-1':A()},[B(date='2026-03-02')])[0]['reason']=='DATE_MISMATCH'
def test_voided_with_b_entry(): assert compare({'REC-1':A(state='VOIDED')},[B()])[0]['reason']=='VOIDED_WITH_B_ENTRY'
