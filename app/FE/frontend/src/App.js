import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { BeforeLogin } from './components/BeforeLogin/BeforeLogin';
import { Select } from './components/Select/Select';
import { MainPage } from './components/MainPage/MainPage';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<BeforeLogin />} />
        <Route path="/select" element={<Select />} />
        <Route path="/bookshelf" element={<MainPage />} />
      </Routes>
    </Router>
  );
}

export default App;
