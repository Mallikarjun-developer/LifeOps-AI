import json, os, sqlite3
from contextlib import contextmanager
from pathlib import Path

DB = Path(os.getenv('LIFEOPS_DB', str(Path(__file__).resolve().parent / 'lifeops.db')))

@contextmanager
def connection():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB, timeout=15)
    db.row_factory = sqlite3.Row
    try:
        db.execute('PRAGMA journal_mode=WAL')
        db.execute('''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, due TEXT DEFAULT '', duration INTEGER DEFAULT 30, priority TEXT DEFAULT 'medium', status TEXT DEFAULT 'todo', scheduled_start TEXT DEFAULT '', scheduled_end TEXT DEFAULT '')''')
        db.execute('''CREATE TABLE IF NOT EXISTS preferences (key TEXT PRIMARY KEY, value TEXT NOT NULL)''')
        db.commit()
        yield db
        db.commit()
    finally: db.close()

def all_tasks():
    with connection() as db:
        return [dict(r) for r in db.execute('SELECT * FROM tasks ORDER BY CASE priority WHEN "high" THEN 0 WHEN "medium" THEN 1 ELSE 2 END, id DESC')]

def add_task(title, due='', duration=30, priority='medium'):
    title = str(title).strip()[:240]
    if not title: raise ValueError('Task title cannot be empty')
    if priority not in ('low','medium','high'): priority='medium'
    duration = max(5, min(480, int(duration)))
    with connection() as db:
        cur=db.execute('INSERT INTO tasks(title,due,duration,priority) VALUES (?,?,?,?)',(title,str(due),duration,priority))
        id=cur.lastrowid
        return dict(db.execute('SELECT * FROM tasks WHERE id=?',(id,)).fetchone())

def update_task(id, **changes):
    allowed={'title','due','duration','priority','status','scheduled_start','scheduled_end'}
    changes={k:v for k,v in changes.items() if k in allowed and v is not None}
    if 'priority' in changes and changes['priority'] not in ('low','medium','high'): raise ValueError('Invalid priority')
    if 'status' in changes and changes['status'] not in ('todo','done'): raise ValueError('Invalid status')
    if 'duration' in changes: changes['duration']=max(5,min(480,int(changes['duration'])))
    if not changes: raise ValueError('No changes')
    with connection() as db:
        db.execute('UPDATE tasks SET '+', '.join(f'{k}=?' for k in changes)+' WHERE id=?', [*changes.values(),int(id)])
        row=db.execute('SELECT * FROM tasks WHERE id=?',(int(id),)).fetchone()
        if row is None: raise ValueError('Task not found')
        return dict(row)

def delete_task(id):
    with connection() as db:
        cur=db.execute('DELETE FROM tasks WHERE id=?',(int(id),))
        return {'deleted':cur.rowcount>0,'id':int(id)}

def get_preferences():
    with connection() as db:
        return {r['key']:json.loads(r['value']) for r in db.execute('SELECT * FROM preferences')}

def set_preference(key,value):
    if key not in ('day_start','day_end','break_minutes'): raise ValueError('Unsupported preference')
    with connection() as db:
        db.execute('INSERT INTO preferences(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,json.dumps(value)))
    return get_preferences()
