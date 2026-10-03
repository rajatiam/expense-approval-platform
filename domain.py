import csv, hashlib, io, json, math, re
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.request import Request, urlopen

def now(): return datetime.now(timezone.utc).isoformat()

def validate(data, records):
    if not isinstance(data,dict): raise ValueError('JSON object required')
    row = {}
    for key,example in CONFIG['example'].items():
        value = data.get(key)
        if isinstance(example,bool):
            if not isinstance(value,bool): raise ValueError(key+' must be boolean')
        elif isinstance(example,(int,float)):
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value < 0: raise ValueError(key+' must be finite and nonnegative')
            if isinstance(example,int) and not isinstance(value,int): raise ValueError(key+' must be an integer')
        elif not isinstance(value,str) or not value.strip() or len(value)>2000: raise ValueError(key+' requires text, up to 2000 characters')
        row[key] = value.strip() if isinstance(value,str) else value
    return initialize(row,records)

def http_url(value):
    url = urlparse(value)
    if url.scheme not in ['http','https'] or not url.hostname or url.username or url.password: raise ValueError('HTTP(S) URL without credentials required')

def unique(rows,row,fields):
    if any(all(r[f]==row[f] for f in fields) for r in rows): raise ValueError('Duplicate '+', '.join(fields))

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
