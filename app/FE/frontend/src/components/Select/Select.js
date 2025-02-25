import React from "react";
import { Frame } from "../Frame/Frame";
import "./Select.css";

export const Select = () => {
  return (
    <section className="select">
      <div className="container">
        <header className="header">
          <h1 className="title">BOOKSELF</h1>
          <p className="subtitle">Please rate the following books</p>
        </header>
        <Frame className="frame" />
      </div>
    </section>
  );
};
