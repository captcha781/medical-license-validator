import React from 'react';
import PropTypes from 'prop-types';
import { Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';

const RouteCondition = (props) => {
  const { type, children } = props;
  let { isAuth } = useSelector((state) => state.auth);

  if (type === 'auth' && isAuth) {
    return <Navigate to="/dashboard" />;
  } else if (type === 'private' && !isAuth) {
    return <Navigate to="/signin" />;
  }

  return children;
};

RouteCondition.propTypes = {
  type: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired
};

export default React.memo(RouteCondition);
