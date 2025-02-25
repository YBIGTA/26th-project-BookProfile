import React, { useState } from "react";
import PropTypes from "prop-types";
import "./BookCard.css";

export const BookCard = ({ imageSrc, title, author, onRatingChange }) => {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);

  const handleRatingClick = (value) => {
    setRating(value);
    if (onRatingChange) {
      onRatingChange(value);
    }
  };

  return (
    <div className="book-card">
      <img className="book-image" src={imageSrc} alt={title} />
      <div className="book-info">
        <h3 className="book-title">{title}</h3>
        <p className="book-author">{author}</p>
        <div className="star-rating">
          {[...Array(5)].map((_, index) => {
            const starValue = index + 1;
            return (
              <button
                type="button"
                key={index}
                className={`star-button ${starValue <= (hover || rating) ? "on" : "off"}`}
                onClick={() => handleRatingClick(starValue)}
                onMouseEnter={() => setHover(starValue)}
                onMouseLeave={() => setHover(rating)}
              >
                <span className="star">★</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
};

BookCard.propTypes = {
  imageSrc: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  author: PropTypes.string.isRequired,
  onRatingChange: PropTypes.func,
};
