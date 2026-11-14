#!/usr/bin/env python3
"""Daymark — local event list and iCalendar (.ics) exporter."""
import argparse,datetime as dt,sqlite3,sys,uuid
from pathlib import Path
DB=Path(__file__).with_name("daymark.db")
def conn():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.execute("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,title TEXT NOT NULL,start TEXT NOT NULL,end TEXT,location TEXT DEFAULT '',notes TEXT DEFAULT '')"); return c
def esc(s): return str(s).replace("\\","\\\\").replace(";","\\;").replace(",","\\,").replace("\n","\\n")
def main():
 p=argparse.ArgumentParser(description="Local calendar and ICS exporter"); s=p.add_subparsers(dest="cmd",required=True)
 a=s.add_parser("add"); a.add_argument("title"); a.add_argument("--start",required=True,help="YYYY-MM-DD or YYYY-MM-DDTHH:MM"); a.add_argument("--end"); a.add_argument("--location",default=""); a.add_argument("--notes",default="")
 l=s.add_parser("list"); l.add_argument("--from",dest="start"); l.add_argument("--to",dest="end")
 x=s.add_parser("export"); x.add_argument("file",nargs="?",default="daymark.ics")
 d=s.add_parser("delete"); d.add_argument("id",type=int)
 args=p.parse_args(); c=conn()
 if args.cmd=="add":
  try: dt.datetime.fromisoformat(args.start)
  except ValueError: sys.exit("Invalid --start format")
  if args.end:
   try: dt.datetime.fromisoformat(args.end)
   except ValueError: sys.exit("Invalid --end format")
  c.execute("INSERT INTO events(title,start,end,location,notes) VALUES(?,?,?,?,?)",(args.title,args.start,args.end,args.location,args.notes)); c.commit(); print("Event created.")
 elif args.cmd=="list":
  sql="SELECT * FROM events WHERE 1=1"; vals=[]
  if args.start: sql+=" AND start>=?"; vals.append(args.start)
  if args.end: sql+=" AND start<=?"; vals.append(args.end)
  for e in c.execute(sql+" ORDER BY start",vals): print(f"[{e['id']}] {e['start']}  {e['title']}"+(f" @ {e['location']}" if e["location"] else ""))
 elif args.cmd=="delete":
  cur=c.execute("DELETE FROM events WHERE id=?",(args.id,)); c.commit(); print("Deleted." if cur.rowcount else "Not found.")
 elif args.cmd=="export":
  lines=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//ERROR404DTIR//Daymark 1.0//EN","CALSCALE:GREGORIAN"]
  for e in c.execute("SELECT * FROM events ORDER BY start"):
   def stamp(v):
    if not v:return ""
    return dt.datetime.fromisoformat(v).strftime("%Y%m%dT%H%M%S") if "T" in v else v.replace("-","")
   lines += ["BEGIN:VEVENT","UID:"+uuid.uuid4().hex+"@daymark.local","DTSTAMP:"+dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),("DTSTART:"+stamp(e["start"])) if "T" in e["start"] else "DTSTART;VALUE=DATE:"+stamp(e["start"])]
   if e["end"]: lines.append(("DTEND:"+stamp(e["end"])) if "T" in e["end"] else "DTEND;VALUE=DATE:"+stamp(e["end"]))
   lines += ["SUMMARY:"+esc(e["title"])]
   if e["location"]: lines.append("LOCATION:"+esc(e["location"]))
   if e["notes"]: lines.append("DESCRIPTION:"+esc(e["notes"]))
   lines.append("END:VEVENT")
  lines.append("END:VCALENDAR")
  Path(args.file).write_text("\r\n".join(lines)+"\r\n",encoding="utf-8"); print("Exported",args.file)
 c.close()
if __name__=="__main__": main()
