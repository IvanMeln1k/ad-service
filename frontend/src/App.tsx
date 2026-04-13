import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import AllAdsPage from './pages/AllAdsPage';
import AdDetailsPage from './pages/AdDetailsPage';
import UserProfilePage from './pages/UserProfilePage';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={
            isAuthenticated ? <Navigate to="/ads" /> : <LoginPage onLogin={() => setIsAuthenticated(true)} />
          } 
        />
        <Route 
          path="/register" 
          element={
            isAuthenticated ? <Navigate to="/ads" /> : <RegisterPage onRegister={() => setIsAuthenticated(true)} />
          } 
        />
        <Route 
          path="/ads" 
          element={
            isAuthenticated ? <AllAdsPage onLogout={() => setIsAuthenticated(false)} /> : <Navigate to="/login" />
          } 
        />
        <Route 
          path="/ads/:id" 
          element={
            isAuthenticated ? <AdDetailsPage onLogout={() => setIsAuthenticated(false)} /> : <Navigate to="/login" />
          } 
        />
        <Route 
          path="/profile" 
          element={
            isAuthenticated ? <UserProfilePage onLogout={() => setIsAuthenticated(false)} /> : <Navigate to="/login" />
          } 
        />
        <Route path="/" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}
