import PropTypes from "prop-types";
import React from "react";
import { Button } from '@mui/material';
import "./FrameLogin.css";

export const FrameLogin = ({ property1, className }) => {
  return (
    <div className={`frame-login ${className}`}>
      <div className="text-wrapper">login</div>
    </div>
  );
};

FrameLogin.propTypes = {
  property1: PropTypes.oneOf(["default"]),
};
