from datetime import datetime, timedelta
from store import all_tasks, update_task, get_preferences

def plan(day=None):
    """Deterministic earliest-deadline-first scheduling; never silently overlap tasks."""
    now=datetime.now().astimezone()
    try: selected=datetime.strptime(day,'%Y-%m-%d').date() if day else now.date()
    except ValueError: raise ValueError('Day must be YYYY-MM-DD')
    prefs=get_preferences()
    start_hour=int(prefs.get('day_start',9)); end_hour=int(prefs.get('day_end',21)); break_mins=int(prefs.get('break_minutes',10))
    if not (0<=start_hour<end_hour<=24 and 0<=break_mins<=120): raise ValueError('Invalid preferences')
    start=datetime.combine(selected,datetime.min.time(),tzinfo=now.tzinfo)+timedelta(hours=start_hour)
    end=datetime.combine(selected,datetime.min.time(),tzinfo=now.tzinfo)+timedelta(hours=end_hour)
    if selected==now.date(): start=max(start,now.replace(second=0,microsecond=0))
    tasks=[t for t in all_tasks() if t['status']=='todo']
    def due_dt(t):
        try: return datetime.fromisoformat(t['due']).replace(tzinfo=now.tzinfo) if t['due'] else None
        except ValueError: return None
    # Tasks with a deadline on another day are excluded unless overdue.
    candidates=[t for t in tasks if not due_dt(t) or due_dt(t).date()<=selected]
    candidates.sort(key=lambda t:(due_dt(t) or datetime.max.replace(tzinfo=now.tzinfo), {'high':0,'medium':1,'low':2}[t['priority']],t['id']))
    scheduled=[]; conflicts=[]; cursor=start
    for t in candidates:
        deadline=due_dt(t)
        finish=cursor+timedelta(minutes=t['duration'])
        if finish>end or (deadline and finish>deadline):
            reason='Outside available hours' if finish>end else 'Cannot finish before deadline'
            conflicts.append({'task_id':t['id'],'title':t['title'],'reason':reason})
            update_task(t['id'],scheduled_start='',scheduled_end='')
            continue
        update_task(t['id'],scheduled_start=cursor.isoformat(timespec='minutes'),scheduled_end=finish.isoformat(timespec='minutes'))
        scheduled.append({'task_id':t['id'],'title':t['title'],'start':cursor.isoformat(timespec='minutes'),'end':finish.isoformat(timespec='minutes')})
        cursor=finish+timedelta(minutes=break_mins)
    return {'day':str(selected),'scheduled':scheduled,'conflicts':conflicts,'timezone':str(now.tzinfo),'note':'Plans tasks sequentially; deadlines use local time. No external calendar is connected.'}
