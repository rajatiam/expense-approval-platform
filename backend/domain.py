import csv, hashlib, io, json, math, re
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from .validation import validate_input, http_url, unique

def now(): return datetime.now(timezone.utc).isoformat()
def validate(data,records): return initialize(validate_input(data,CONFIG['example']),records)

from decimal import Decimal
def initialize(row,records):
    unique(records,row,['reference'])
    if row['amount'] <= 0: raise ValueError('Amount must be positive')
    row['amount'] = float(Decimal(str(row['amount'])).quantize(Decimal('0.01')))
    return dict(row,status='pending')
def summary(rows):
    total = sum((Decimal(str(r['amount'])) for r in rows if r['status']=='approved'),Decimal('0'))
    return {'expenses':len(rows),'approved_spend':float(total),'pending':sum(r['status']=='pending' for r in rows),'over_budget':sum(r['amount']>r['budget'] for r in rows)}
def transition(row,action):
    if action not in ['approve','reject'] or row['status']!='pending': raise ValueError('Only pending expenses can be approved or rejected')
    if action=='approve' and row['amount']>row['budget']: raise ValueError('Expense exceeds approval budget')
    return dict(row,status='approved' if action=='approve' else 'rejected')
