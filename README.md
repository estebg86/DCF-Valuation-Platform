[README.md](https://github.com/user-attachments/files/26520942/README.md)
# DCF Valuation Platform - Cloud Edition ☁️

**100% cloud-deployed. Zero local installation required.**

Professional DCF (Discounted Cash Flow) valuation platform that runs entirely in the cloud using free services.

## 🌐 Live Demo

After deployment, you'll have:
- **Frontend**: https://your-app.vercel.app
- **Backend API**: https://your-backend.railway.app
- **API Docs**: https://your-backend.railway.app/docs

## ✨ Features

✅ **Automated SEC EDGAR data fetching**  
✅ **Comprehensive 10-year DCF projections**  
✅ **WACC calculation using CAPM**  
✅ **Sensitivity analysis**  
✅ **Interactive charts and visualizations**  
✅ **Professional valuation in seconds**  

## 🚀 Quick Deploy (3 Steps)

### 1. Upload to GitHub
- Create new public repository
- Upload `backend/` and `frontend/` folders

### 2. Deploy Backend (Railway/Render)
- Connect GitHub repository
- Select `backend` folder
- Auto-deploys!

### 3. Deploy Frontend (Vercel)
- Connect GitHub repository
- Select `frontend` folder
- Add environment variable: `NEXT_PUBLIC_API_URL`
- Deploy!

**Full guide:** See `DEPLOYMENT_GUIDE.md`

## 📁 Project Structure

```
dcf-platform-cloud/
├── backend/                # Python FastAPI backend
│   ├── main.py            # API server
│   ├── sec_fetcher.py     # SEC data retrieval
│   ├── dcf_model.py       # Valuation engine
│   ├── requirements.txt   # Python dependencies
│   ├── Procfile           # Railway/Render config
│   ├── runtime.txt        # Python version
│   └── .env.example       # Environment template
│
├── frontend/              # React/Next.js frontend
│   ├── pages/            # Next.js pages
│   ├── components/       # React components
│   ├── package.json      # Node dependencies
│   ├── vercel.json       # Vercel config
│   └── .env.example      # Environment template
│
├── DEPLOYMENT_GUIDE.md   # Detailed deployment steps
└── QUICK_REFERENCE.md    # Quick reference card
```

## 🔧 Technology Stack

**Backend:**
- Python 3.11 + FastAPI
- pandas, numpy, scipy
- SEC EDGAR API (free)

**Frontend:**
- Next.js 14 + React 18
- Tailwind CSS
- Recharts

**Hosting:**
- Railway/Render (Backend)
- Vercel (Frontend)
- GitHub (Code repository)

## 💰 Costs

**Total: $0-2/month**

- Railway: $5 free credit/month
- Render: Free tier (spins down)
- Vercel: Unlimited free
- GitHub: Free for public repos

## 📊 What You Can Do

After deployment:

1. **Value any US public company** (MSFT, AAPL, GOOGL, etc.)
2. **Customize assumptions** (growth rates, WACC, margins)
3. **Run sensitivity analysis** (test different scenarios)
4. **Share with colleagues** (just send the URL!)
5. **Access from anywhere** (any device with browser)

## 🎯 Perfect For

- Finance students learning DCF
- Analysts doing quick valuations
- Investors researching companies
- Educators teaching financial modeling
- Anyone wanting institutional-quality valuations

## ⚡ Performance

- **First valuation**: 5-15 seconds
- **Subsequent**: Faster (cached)
- **Render free tier**: +30s cold start
- **Railway**: No cold starts

## 📚 Documentation

- **`DEPLOYMENT_GUIDE.md`** - Complete deployment walkthrough
- **`QUICK_REFERENCE.md`** - Quick commands and troubleshooting
- **`backend/.env.example`** - Backend environment variables
- **`frontend/.env.example`** - Frontend environment variables

## 🆘 Support

**Deployment Issues:**
1. Check `DEPLOYMENT_GUIDE.md`
2. Verify environment variables
3. Check service logs (Railway/Render/Vercel)

**API Issues:**
- Visit `/docs` endpoint for interactive API testing
- Check `/health` endpoint for backend status

**Test with:**
- MSFT (Microsoft) - Always works
- AAPL (Apple)
- GOOGL (Google)
- NVDA (NVIDIA)

## ⚠️ Important Notes

### Educational Use Only
This platform is for educational and research purposes. Not financial advice.

### SEC Data
- Uses official SEC EDGAR API (free)
- US companies only
- Historical data only
- Requires valid ticker symbols

### Free Tier Limitations
- **Railway**: 500 hours/month
- **Render**: Spins down after 15min idle
- **Vercel**: Unlimited, but fair use

## 🔐 Environment Variables

### Backend (Railway/Render)
```bash
FRONTEND_URL=https://your-app.vercel.app
ENVIRONMENT=production
```

### Frontend (Vercel)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

## 🔄 Updates

**To update deployed app:**

```bash
# Make changes locally
git add .
git commit -m "Description"
git push

# Auto-deploys to all services!
```

## ✅ Deployment Checklist

- [ ] GitHub repository created
- [ ] Backend deployed (Railway/Render)
- [ ] Backend URL copied
- [ ] Frontend deployed (Vercel)
- [ ] Environment variables configured
- [ ] Frontend URL works
- [ ] Backend /health endpoint returns OK
- [ ] Test valuation completes (try MSFT)

## 🎓 Learning Resources

**DCF Methodology:**
- Aswath Damodaran's NYU lectures
- CFA Institute curriculum
- SEC EDGAR data structure

**Platform Architecture:**
- FastAPI documentation
- Next.js documentation
- SEC EDGAR API guide

## 📈 Example Output

```
MICROSOFT CORPORATION (MSFT)
─────────────────────────────
Enterprise Value:    $1,994B
Equity Value:        $2,014B
Value per Share:     $271.00
Current Price:       $380.00
Upside/(Downside):   -28.7%

WACC:                8.42%
Terminal Growth:     2.5%
```

## 🌟 Features Roadmap

Current:
✅ DCF valuation
✅ Sensitivity analysis
✅ Historical data
✅ Cloud deployment

Future:
- [ ] Monte Carlo simulation
- [ ] Multiple scenarios
- [ ] PDF report export
- [ ] Comparable company analysis

## 📄 License

Educational use. See individual components for specific licenses.

## 🤝 Contributing

Improvements welcome! Focus areas:
- Additional valuation methods
- UI enhancements
- Documentation improvements
- Bug fixes

## 🎉 Get Started

1. **Read**: `DEPLOYMENT_GUIDE.md`
2. **Deploy**: Follow the 3 steps
3. **Test**: Value MSFT
4. **Customize**: Adjust assumptions
5. **Share**: Send URL to colleagues!

---

**Built for finance professionals, powered by the cloud. 📊🚀**

**Questions?** Check `DEPLOYMENT_GUIDE.md` for detailed instructions.
