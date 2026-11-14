# Daymark

<p align="center"><img src="assets/banner.svg" alt="Daymark animated banner" width="100%"></p>

A local calendar CLI for capturing events and exporting a standards-based iCalendar file for common calendar applications.

## Features
- Events with date/date-time, location and notes
- List events within an optional date range
- Delete events by ID
- Export to `.ics`
- SQLite storage; Python standard library only

## Run
Python 3.9+:

```bash
python app.py add "Project review" --start 2026-12-02T15:30 --end 2026-12-02T16:00 --location "Room 4"
python app.py add "Holiday" --start 2026-12-24
python app.py list
python app.py list --from 2026-12-01 --to 2026-12-31
python app.py export calendar.ics
python app.py delete 1
```

The database `daymark.db` is created beside the script. Date-times are stored as local wall-clock values; timezone conversion is left to your calendar application.