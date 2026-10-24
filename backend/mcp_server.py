from mcp.server.fastmcp import FastMCP
from store import add_task, all_tasks, update_task, delete_task, get_preferences, set_preference
from planner import plan

mcp=FastMCP('LifeOps AI', stateless_http=True, json_response=True, host='127.0.0.1', port=8000)

@mcp.tool()
def create_task(title:str, due:str='', duration:int=30, priority:str='medium')->dict:
    """Create a task. due is optional local ISO datetime, e.g. 2026-10-23T17:00."""
    return add_task(title,due,duration,priority)

@mcp.tool()
def list_tasks()->list[dict]:
    """Read persisted tasks."""
    return all_tasks()

@mcp.tool()
def edit_task(task_id:int, title:str|None=None, due:str|None=None, duration:int|None=None, priority:str|None=None, status:str|None=None)->dict:
    """Edit a task; set status to done to complete it."""
    return update_task(task_id,title=title,due=due,duration=duration,priority=priority,status=status)

@mcp.tool()
def remove_task(task_id:int)->dict:
    """Delete a task by id."""
    return delete_task(task_id)

@mcp.tool()
def replan_schedule(day:str='')->dict:
    """Schedule incomplete tasks on a day (YYYY-MM-DD), detect conflicts, and save changes."""
    return plan(day or None)

@mcp.tool()
def save_preference(key:str,value:str)->dict:
    """Set day_start, day_end (hour 0-24) or break_minutes (integer)."""
    return set_preference(key,int(value))

@mcp.tool()
def read_preferences()->dict:
    """Read saved scheduling preferences."""
    return get_preferences()

if __name__=='__main__':
    mcp.run(transport='streamable-http')
