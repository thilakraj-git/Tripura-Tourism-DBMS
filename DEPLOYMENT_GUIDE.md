   * **Start Command:** `python run_server.py`
   * **Plan:** `Free`
6. Click **"Create Web Service"**.
7. Render will build and deploy your site, giving you a live public URL like:
   `https://tripura-tourism.onrender.com`

---

## 🚂 Option 2: Deploy on Railway.app

1. Go to **[Railway.app](https://railway.app/)** and log in with GitHub.
2. Click **"New Project"** → **"Deploy from GitHub repo"**.
3. Select your repository.
4. Railway will automatically detect `Procfile` and `requirements.txt` and launch the service!
5. In **Settings** → **Networking**, click **"Generate Domain"** to get a public URL like:
   `https://tripura-tourism.up.railway.app`

---

## 🐳 Option 3: Deploy with Docker

If you have Docker installed or are deploying to a VPS (DigitalOcean, AWS, GCP, Linode):

1. **Build the container image:**
   ```bash
   docker build -t tripura-tourism .
   ```
2. **Run the container:**
   ```bash
   docker run -d -p 8000:8000 --name tripura-app tripura-tourism
   ```
3. Visit `http://your-server-ip:8000`.

---

## 📁 Key Deployment Files Created
* `requirements.txt`: Python package specifications
* `Procfile`: Command executed by web servers (`web: python run_server.py`)
* `Dockerfile`: Containerized deployment recipe
* `render.yaml`: 1-click Render blueprint
* `.dockerignore`: Excludes cache and local files from production image
