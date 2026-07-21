# System Architecture

## Overview

The Customer Intelligence Platform follows a three-tier architecture consisting of:

- Presentation Layer (React)
- Application Layer (FastAPI)
- Data Layer (PostgreSQL)

The machine learning module integrates with the backend to calculate RFM metrics and perform customer segmentation using K-Means clustering.

## Technology Stack

- Frontend: React + Vite + Tailwind CSS
- Backend: FastAPI
- Authentication: Supabase Auth
- Database: PostgreSQL (Supabase)
- Machine Learning: Scikit-learn
- Data Processing: Pandas & NumPy
- Charts: Recharts
- Frontend Deployment: Vercel
- Backend Deployment: Render

## Architecture Principles

- RESTful API communication
- Modular backend design
- Secure authentication
- Automatic customer segmentation
- Responsive dashboard