import React, { useState } from 'react';
import AdminInterface from './AdminInterface';
import './AdminPage.css';

const AdminPage = ({ onLogout, onBackToHome }) => {
  return (
    <div className="admin-page">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
        <div className="admin-nav">
          <button onClick={onBackToHome} className="nav-btn">
            🏠 Home
          </button>
          <button onClick={onLogout} className="nav-btn logout-btn">
            🚪 Logout
          </button>
        </div>
      </div>
      <div className="admin-content">
        <AdminInterface />
      </div>
    </div>
  );
};

export default AdminPage;