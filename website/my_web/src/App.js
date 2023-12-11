import React from 'react';
import './App.css';
import Home from './Componnent/Home';
import Rule from './Componnent/Rule';
import { Link, BrowserRouter as Router, Route, Routes } from 'react-router-dom';

function App() {
  return (
    <Router>
      <nav>
        <ul>
          <NavItem to="/">Home</NavItem>
        </ul>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/rules" element={<Rule />} />
      </Routes>
    </Router>
  );
}

// A custom navigation item component for consistency
function NavItem({ to, children }) {
  return (
    <li>
      <Link to={to}>{children}</Link>
    </li>
  );
}

export default App;
