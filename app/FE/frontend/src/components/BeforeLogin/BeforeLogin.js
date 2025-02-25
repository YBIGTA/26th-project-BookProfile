import { Button, TextField } from "@mui/material";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FrameLogin } from "../FrameLogin/FrameLogin";
import "./style.css";

export const BeforeLogin = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    id: "",
    password: "",
  });

  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [id]: value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // TODO: Implement actual login logic here
    navigate('/select'); // Navigate to select page after login
  };

  return (
    <div className="before-login">
      <div className="container">
        <header className="header">
          <h1 className="title">BOOKSELF</h1>
          <p className="subtitle">"Introduce yourself through books!"</p>
        </header>

        <form className="login-form" onSubmit={handleSubmit}>
          <label className="label" htmlFor="id">
            ID
          </label>
          <TextField
            id="id"
            variant="outlined"
            placeholder="Enter your ID"
            fullWidth
            value={formData.id}
            onChange={handleChange}
          />

          <label className="label" htmlFor="password">
            PASSWORD
          </label>
          <TextField
            id="password"
            type="password"
            variant="outlined"
            placeholder="Enter your password"
            fullWidth
            value={formData.password}
            onChange={handleChange}
          />

          <Button 
            className="login-button" 
            variant="contained" 
            color="inherit"
            type="submit"
          >
            login
          </Button>
        </form>

        <FrameLogin className="frame-login" property1="default" />
      </div>
    </div>
  );
};
