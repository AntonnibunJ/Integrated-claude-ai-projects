# IdeaLink
1. `mysql -u root -p < schema.sql`
2. `pip install -r requirements.txt`
3. Set `DB_USER`, `DB_PASS` (and `SECRET_KEY`), then `python app.py`
4. Open http://127.0.0.1:5000
Admin: answer tickets with `UPDATE tickets SET status='resolved', reply='...' WHERE id=1;`
