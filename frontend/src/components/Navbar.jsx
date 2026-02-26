import React from "react";
import { NavLink } from "react-router-dom";

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="container-row">
        <div className="brand">CodePulse AI</div>
        <nav className="nav-links">
          <NavLink to="/" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
            Code
          </NavLink>
          <NavLink to="/analysis" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
            Analysis & Tests
          </NavLink>
          <NavLink to="/optimize" className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}>
            Optimization
          </NavLink>
        </nav>
      </div>
    </header>
  );
}
