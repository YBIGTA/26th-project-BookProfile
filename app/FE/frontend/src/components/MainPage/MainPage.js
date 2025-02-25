import React from "react";
import { User } from "./User/User";
import "./style.css";

export const MainPage = () => {
  return (
    <div className="page">
      <header className="header">
        <h1 className="title">MY BOOKSELF</h1>
      </header>

      <div className="main-content">
        <div className="profile-section">
          <div className="graph-container">
            <div className="graphbox" />
          </div>
          <div className="profile-info">
            <p className="profile-text">
              You're a reader with a passion<br />
              for poetry and drama.
            </p>
            <div className="recent-books">
              <h3 className="recent-books-title">Recent books</h3>
              <div className="books-grid">
                <img src="/book1.jpg" alt="Book 1" className="book-cover" />
                <img src="/book2.jpg" alt="Book 2" className="book-cover" />
                <img src="/book3.jpg" alt="Book 3" className="book-cover" />
                <img src="/book4.jpg" alt="Book 4" className="book-cover" />
              </div>
            </div>
          </div>
        </div>

        <section className="recommendation">
          <h2 className="recommendation-title">
            Ask what you want to read today
          </h2>
          <div className="input-container">
            <span className="arrow-icon">→</span>
            <input
              className="recommendation-input"
              type="text"
              placeholder="Recommend me a novel about ......"
            />
          </div>
        </section>

        <section className="social-section">
          <h2 className="social-title">Follow and Read together</h2>
          <div className="user-matches">
            <User
              className="user-bubble"
              text="@joshuaa"
              text1="90% match"
              style={{ backgroundColor: 'white' }}
            />
            <User
              className="user-bubble"
              text="@ashili"
              text1="75% match"
              style={{ backgroundColor: '#E8F3D6' }}
            />
            <User
              className="user-bubble"
              text="@taesan"
              text1="70% match"
              style={{ backgroundColor: '#DCEFF9' }}
            />
            <User
              className="user-bubble"
              text="@kevin"
              text1="80% match"
              style={{ backgroundColor: '#F8E4FF' }}
            />
            <User
              className="user-bubble"
              text="@emily"
              text1="95% match"
              style={{ backgroundColor: '#FFE4E4' }}
            />
          </div>
          <div className="follow-section">
            <button className="follow-all">follow all</button>
            <button className="refresh-button">
              <img src="/refresh-icon.svg" alt="Refresh" className="refresh-icon" />
            </button>
          </div>
        </section>
      </div>
    </div>
  );
};
