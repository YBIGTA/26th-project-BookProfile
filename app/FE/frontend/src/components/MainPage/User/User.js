import PropTypes from "prop-types";
import React from "react";
import "./user.css";

export const User = ({ className, text, text1, style }) => {
  return (
    <div className={`user ${className}`} style={style}>
      <div className="user-content">
        <div className="username">{text}</div>
        <div className="match-percentage">{text1}</div>
      </div>
    </div>
  );
};

User.propTypes = {
  text: PropTypes.string,
  text1: PropTypes.string,
  className: PropTypes.string,
  style: PropTypes.object,
};
