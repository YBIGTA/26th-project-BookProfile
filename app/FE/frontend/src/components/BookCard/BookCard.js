import PropTypes from "prop-types";
import React from "react";
import "./BookCard.css";

export const BookCard = ({ imageSrc, title, author, description, rating }) => {
  return (
    <article className="book-card">
      <img className="book-image" src={imageSrc} alt={title} />

      <div className="book-details">
        <div className="book-header">
          <h2 className="book-title">{title}</h2>
          <p className="book-author">{author}</p>
        </div>
        <p className="book-description">{description}</p>
      </div>

      <div className="book-rating">
        {[...Array(5)].map((_, index) => (
          <span key={index} className={`star ${index < rating ? "filled" : ""}`}>
            ★
          </span>
        ))}
      </div>
    </article>
  );
};

BookCard.propTypes = {
  imageSrc: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  author: PropTypes.string.isRequired,
  description: PropTypes.string.isRequired,
  rating: PropTypes.number.isRequired,
};
