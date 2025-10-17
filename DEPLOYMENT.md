# Deployment Guide

## Self-Contained Deployment

This Streamlit app is fully self-contained and automatically initializes its database on startup. No manual setup required!

## What Happens on First Run

1. App checks if `pnc_demo.db` exists
2. If not, creates database and seeds with demo data automatically
3. App starts and displays 3 demo insurance cases

## Local Deployment

```bash
cd src
streamlit run app.py
```

That's it! The database auto-creates on first launch.

## Cloud Deployment

### Streamlit Cloud

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Insurance system with auto-init"
   git push
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set main file path: `src/app.py`
   - Click "Deploy"

3. **Done!** The database auto-initializes on first deployment.

### Heroku

1. **Create `Procfile`** in project root:
   ```
   web: cd src && streamlit run app.py --server.port=$PORT
   ```

2. **Deploy**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Docker

1. **Create `Dockerfile`**:
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY src/ ./src/
   
   WORKDIR /app/src
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app.py", "--server.port=8501"]
   ```

2. **Build and run**:
   ```bash
   docker build -t insurance-system .
   docker run -p 8501:8501 insurance-system
   ```

### AWS/Google Cloud/Azure

Deploy as a containerized app using the Docker approach above, or:

1. Use managed app services (Elastic Beanstalk, Cloud Run, App Service)
2. Point to `src/app.py` as entry point
3. Install dependencies from `requirements.txt`
4. Database auto-initializes on first request

## Database Persistence

### For Production Use

The current setup uses SQLite with demo data that auto-seeds. For production:

**Option 1: Keep SQLite (Simple)**
- SQLite file persists in the container/instance
- Good for demos and small deployments
- Mount a volume in Docker for persistence

**Option 2: Use PostgreSQL (Scalable)**
- Modify `seed_database.py` to use PostgreSQL connection
- Set database URL via environment variable
- Use managed database service (RDS, Cloud SQL, etc.)

Example environment variable approach:
```python
# In seed_database.py
DB_URL = os.getenv('DATABASE_URL', 'sqlite:///pnc_demo.db')
engine = create_engine(DB_URL)
```

## Environment Variables

The app works out-of-the-box with no configuration. Optional overrides:

- `DATABASE_URL` - Custom database connection (default: SQLite)
- `PORT` - Server port for cloud platforms (default: 8501)

## Troubleshooting

**Database not seeding?**
- Check logs for initialization messages
- Delete `pnc_demo.db` and restart app

**Permission errors?**
- Ensure write permissions in app directory
- For cloud: some platforms have read-only filesystems - use external database

**Import errors?**
- Ensure working directory is `src/` when running
- Or add `src/` to PYTHONPATH

## Demo Data

The app auto-seeds with 3 realistic insurance cases:

1. **Bäckerei Frischknecht GmbH** - SME with liability claim
2. **Maschinenbau Schmidt AG** - Mid-sized with co-insurance
3. **HelvetiaPharma SA** - Large corp with reinsurance tower

Perfect for demos, POCs, and development!

## Production Checklist

- [ ] Replace SQLite with production database (PostgreSQL/MySQL)
- [ ] Add authentication/authorization
- [ ] Remove or protect seed data functionality
- [ ] Add error tracking (Sentry, etc.)
- [ ] Configure HTTPS/SSL
- [ ] Set up monitoring and logging
- [ ] Configure backups
- [ ] Add rate limiting if publicly accessible

---

**The app is designed to "just work" on any platform!** 🚀

